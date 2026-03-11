class FusionEngine:
    def calculate_final_score(self, ml_score: float, llm_prob: float):
        """
        Fuses Classical ML scores with LLM reasoning probability.
        Weights: ML (50%), LLM (50%)
        Note: ml_score is expected to be pre-weighted (max 0.5) from MLLayer.
        """
        # Formula: Final Score = ml_score (max 0.5) + (0.5 * llm_prob)
        # This keeps the final score in range [0, 1]
        weighted_llm = 0.5 * llm_prob
        final_score = ml_score + weighted_llm
        
        print(f"DEBUG: Fusion Calculation -> (ML:{ml_score:.2f}) + (LLM:{llm_prob:.2f} * 0.5) = Final Score: {final_score:.2f}")
        
        return {
            "final_score": float(final_score),
            "ml_weight": 0.5,
            "llm_weight": 0.5,
            "verdict": self._get_verdict(final_score)
        }

    def _get_verdict(self, score: float):
        # 0.5 is the threshold for binary classification
        if score >= 0.5:
            return "HOAX"
        else:
            return "BUKAN HOAX"
