import logging
import analyzer.log_config as log_config
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

### 로그

logger = logging.getLogger(__name__)

### 감성분석 클래스 생성

class NewsSentimentAnalyzer:

    def __init__(self):
        try:
            logger.info("로컬 감성 모델 로딩 시작")

            self.tokenizer = AutoTokenizer.from_pretrained(
                "daekeun-ml/koelectra-small-v3-nsmc"
            )
            self.model = AutoModelForSequenceClassification.from_pretrained(
                "daekeun-ml/koelectra-small-v3-nsmc"
            )

            logger.info("모델 로딩 완료")

            self.pos_words = ['상승', '호재', '상승세', '회복', '성장', '긍정', '돌파', '유치', '증가', '최고']
            self.neg_words = ['하락', '악재', '하락세', '위기', '감소', '부정', '붕괴', '손실', '최저', '둔화']

        except Exception:
            logger.exception("모델 초기화 중 오류 발생")
            raise

    def sentiment_by_keyword(self, text):
        pos_count = sum(word in text for word in self.pos_words)
        neg_count = sum(word in text for word in self.neg_words)

        if pos_count > neg_count:
            return 1
        elif neg_count > pos_count:
            return 0
        else:
            return None

    def predict(self, text):

        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )

            with torch.no_grad():
                outputs = self.model(**inputs)

            probs = torch.softmax(outputs.logits, dim=1)
            model_score = probs[0][1].item()

            keyword_result = self.sentiment_by_keyword(text)

            if keyword_result is not None:
                final_score = 0.7 * model_score + 0.3 * keyword_result
            else:
                final_score = model_score

            if final_score > 0.6:
                label = "긍정"
            elif final_score < 0.4:
                label = "부정"
            else:
                label = "중립"

            logger.info(f"예측 완료 | 결과: {label} | 점수: {final_score:.4f}")

            return label, final_score

        except Exception:
            logger.exception("예측 중 오류 발생")
            return "error", 0.0
