"""Hệ thống biện chứng luận trị YHCT (ComboBox tầng 1 + CBM + KG) - bản web Flask.

Phần tri thức (KG) và mạng nơ-ron giữ nguyên logic của bản Tkinter (SYM_GUI_CBM_KG.py).
"""
import os

import networkx as nx
import numpy as np
from flask import Flask, jsonify, render_template, request


# ==========================================
# 1. CƠ SỞ TRI THỨC VÀ MÔ HÌNH (KG & CBM)
# ==========================================
class YHCTKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        tri_thuc = [
            # 1. Thận Âm Hư
            ("Sốt chiều", "HỘI_CHỨNG", "Thận Âm Hư"),
            ("Triều nhiệt", "HỘI_CHỨNG", "Thận Âm Hư"),
            ("Nhức trong xương", "HỘI_CHỨNG", "Thận Âm Hư"),
            ("Lưỡi đỏ ít rêu", "HỘI_CHỨNG", "Thận Âm Hư"),
            ("Mạch tế sác", "HỘI_CHỨNG", "Thận Âm Hư"),
            ("Lòng bàn tay chân nóng", "HỘI_CHỨNG", "Thận Âm Hư"),
            ("Đêm ra mồ hôi trộm", "HỘI_CHỨNG", "Thận Âm Hư"),
            ("Thận Âm Hư", "BÀI_THUỐC", "Lục Vị Địa Hoàng Hoàn"),
            # 2. Can Khí Uất Kết
            ("Ngực sườn đầy tức", "HỘI_CHỨNG", "Can Khí Uất Kết"),
            ("Hay thở dài", "HỘI_CHỨNG", "Can Khí Uất Kết"),
            ("Tính tình thất thường", "HỘI_CHỨNG", "Can Khí Uất Kết"),
            ("Rêu lưỡi mỏng", "HỘI_CHỨNG", "Can Khí Uất Kết"),
            ("Mạch huyền", "HỘI_CHỨNG", "Can Khí Uất Kết"),
            ("Can Khí Uất Kết", "BÀI_THUỐC", "Tiêu Dao Tản"),
            # 3. Tỳ Vị Hư Hàn
            ("Đau bụng âm ỉ", "HỘI_CHỨNG", "Tỳ Vị Hư Hàn"),
            ("Thích chườm nóng xoa ấm", "HỘI_CHỨNG", "Tỳ Vị Hư Hàn"),
            ("Tỳ Vị Hư Hàn", "BÀI_THUỐC", "Hoàng Cửu Kiện Trung Thang"),
            # 4. Phế Nhiệt
            ("Ho khạc đờm vàng đặc", "HỘI_CHỨNG", "Phế Nhiệt"),
            ("Sốt khát nước", "HỘI_CHỨNG", "Phế Nhiệt"),
            ("Phế Nhiệt", "BÀI_THUỐC", "Ma Hoàng Hạnh Nhân Cam Thảo Thạch Cao Thang"),
        ]
        for source, relation, target in tri_thuc:
            self.graph.add_edge(source, target, relation=relation)

    def query_diagnosis(self, active_concepts):
        scores, explanations = {}, {}
        for concept in active_concepts:
            if concept in self.graph:
                for neighbor in self.graph.neighbors(concept):
                    if self.graph[concept][neighbor]["relation"] == "HỘI_CHỨNG":
                        scores[neighbor] = scores.get(neighbor, 0) + 1
                        explanations.setdefault(neighbor, []).append(concept)
        if not scores:
            return None, [], {}
        best = max(scores, key=scores.get)
        treatments = [t for t in self.graph.neighbors(best)
                      if self.graph[best][t]["relation"] == "BÀI_THUỐC"]
        return best, treatments, explanations


# ==========================================
# 2. MẠNG NEURAL CHUẨN HÓA BIAS ĐỂ LỌC ĐÚNG XÁC SUẤT 0.00
# ==========================================
class KGTrainedNeuralPredictor:
    def __init__(self, kg, concept_names):
        self.kg = kg
        self.concept_names = concept_names
        self.input_dim = len(concept_names)
        self.W = np.eye(self.input_dim) * 3.5
        syn = {c: {n for n in kg.graph.neighbors(c) if kg.graph[c][n]["relation"] == "HỘI_CHỨNG"}
               for c in concept_names}
        for i, c1 in enumerate(concept_names):
            for j, c2 in enumerate(concept_names):
                if i != j and syn[c1] & syn[c2]:
                    self.W[i, j] = 0.3
        self.bias = np.full(self.input_dim, -1.8)

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    def predict_concepts(self, raw_features):
        probs = self.sigmoid(np.dot(raw_features, self.W) + self.bias)
        return {name: float(probs[i]) for i, name in enumerate(self.concept_names)}


kg = YHCTKnowledgeGraph()
CONCEPTS = sorted({u for u, v, d in kg.graph.edges(data=True) if d.get("relation") == "HỘI_CHỨNG"})
predictor = KGTrainedNeuralPredictor(kg, CONCEPTS)
PROB_VALUES = ["0.00", "0.10", "0.20", "0.30", "0.40", "0.50", "0.60", "0.70", "0.80", "0.85", "0.90", "1.00"]
TRIPLES = [(u, d["relation"], v) for u, v, d in kg.graph.edges(data=True)]
LINE = "=" * 73


def build_report(raw, threshold):
    """Tạo nội dung 3 tầng như hàm run_prediction của bản Tkinter. Mỗi dòng: {t: chữ, hl: tô xanh}."""
    probs = predictor.predict_concepts(np.array([raw[c] for c in CONCEPTS]))
    passed = {c: p for c, p in probs.items() if p >= threshold}
    syndrome, treatments, expl = kg.query_diagnosis(list(passed))
    out = []
    add = lambda t, hl=False: out.append({"t": t, "hl": hl})

    add(LINE); add(f"  [TẦNG 1]: RAW INPUT LAYER (Chỉ hiển thị triệu chứng P ≥ {threshold:.2f})"); add(LINE)
    n1 = 0
    for c in CONCEPTS:
        if probs[c] >= threshold:
            n1 += 1
            add(f" • {c:<26} | X_raw (Combo) = {raw[c]:.2f} | P = {probs[c]:.2f} --> [✓ Lọt qua]", True)
    if n1 == 0:
        add(" ⚠️ Không có triệu chứng nào ở Tầng 1 đạt ngưỡng xác suất!")

    add(""); add(LINE); add(f"  [TẦNG 2]: CONCEPT BOTTLENECK LAYER (Chỉ hiện P ≥ {threshold:.2f})"); add(LINE)
    if passed:
        for c, p in passed.items():
            add(f" [Khái niệm]: {c:<26} (Probability = {p:.2f})", True)
    else:
        add(" ⚠️ Không có khái niệm nào vượt qua ngưỡng Bottleneck!")

    add(""); add(LINE); add("  [TẦNG 3]: KG INFERENCE & EXPLANATION LAYER (Chẩn Đoán Động)"); add(LINE)
    if not syndrome:
        add(" ⚠️ Không thể kết luận hội chứng dựa trên các khái niệm đã chọn.")
    else:
        add(f" 🩺 HỘI CHỨNG DỰ ĐOÁN  : {syndrome}")
        add(f" 💊 BÀI THUỐC ĐỀ XUẤT  : {', '.join(treatments) if treatments else 'N/A'}")
        add(""); add(" 🔍 ĐƯỜNG DẪN GIẢI THÍCH CHẨN ĐOÁN (Explanation Path):")
        for s in expl.get(syndrome, []):
            add(f"   ↳ ({s} [P={probs.get(s, 0.0):.2f}]) --[CHỈ_RA]--> ({syndrome})")
        for t in treatments:
            add(f"   ↳ ({syndrome}) --[ĐIỀU_TRỊ_BẰNG]--> (Bài thuốc: {t})")
    return {"lines": out, "syndrome": syndrome, "treatments": treatments}


# ==========================================
# 3. WEB
# ==========================================
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", concepts=CONCEPTS, prob_values=PROB_VALUES, triples=TRIPLES)


@app.route("/api/diagnose", methods=["POST"])
def api_diagnose():
    data = request.get_json(silent=True) or {}
    try:
        threshold = max(0.0, min(1.0, float(data.get("threshold", 0.5))))
    except (TypeError, ValueError):
        return jsonify(error="Ngưỡng không hợp lệ!"), 400
    inputs, raw = data.get("inputs") or {}, {}
    for c in CONCEPTS:
        try:
            raw[c] = max(0.0, min(1.0, float(inputs.get(c, "0.00"))))
        except (TypeError, ValueError):
            return jsonify(error=f"Giá trị ComboBox của '{c}' không hợp lệ!"), 400
    return jsonify(build_report(raw, threshold))


@app.route("/healthz")
def healthz():
    return "ok"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=True)
