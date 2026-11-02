import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from dotenv import load_dotenv

from .schemas import ProductInput
from .service import generate_card, GenerationError

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="AI Product Card Assistant", version="1.0.0",
              description="Генератор SEO-карточек КИП для B2B-магазина")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    example = {
        "name": "Манометр показывающий DM 02",
        "manufacturer": "Манотомь",
        "specs": {
            "диапазон измерений": "0–1,6 МПа",
            "класс точности": "1,5",
            "присоединение": "G1/2",
            "диаметр корпуса": "100 мм"
        },
        "description": "Прибор предназначен для измерения избыточного давления."
    }
    return templates.TemplateResponse(request=request, name="index.html",
                                       context={"example": json.dumps(example, ensure_ascii=False, indent=2)})


@app.post("/api/generate")
def generate(payload: dict):
    try:
        product = ProductInput.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False))
    try:
        card = generate_card(product)
        return JSONResponse({"product": product.model_dump(), "card": card.model_dump()})
    except GenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/api/generate-markdown", response_class=JSONResponse)
def generate_markdown(payload: dict):
    try:
        product = ProductInput.model_validate(payload)
        card = generate_card(product)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False))
    except GenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    md = [f"# {card.seo_title}", "", f"**SEO-описание**\n\n{card.seo_description}", "",
          "## Характеристики"]
    md.extend(f"- **{k}:** {v}" for k, v in card.key_characteristics.items())
    md += ["", "## Поисковые запросы"]
    md.extend(f"- {q}" for q in card.search_queries)
    md += ["", "## Для менеджера", card.commercial_block, "", "## Не хватает данных"]
    md.extend(f"- {x}" for x in card.missing_data)
    md += ["", "## Уточнить", *[f"- {x}" for x in card.clarification_notes]]
    return {"markdown": "\n".join(md)}
