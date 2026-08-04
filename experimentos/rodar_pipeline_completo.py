import os

from crewai import LLM

from cotton_market_crew.pipeline import montar_pipeline
from cotton_market_crew.store import MercadoStore


def main() -> None:
    llm = LLM(
        model="gemini/gemini-2.5-flash",
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.2,
    )
    store = MercadoStore()
    crew = montar_pipeline(store, llm)

    resultado = crew.kickoff()

    print(f"\n{'=' * 60}\nSAÍDAS INDIVIDUAIS DAS TASKS\n{'=' * 60}")
    for task_output in resultado.tasks_output:
        print(f"\n--- {task_output.agent} ---")
        print(task_output.pydantic)

    print(f"\n{'=' * 60}\nBOLETIM CONSOLIDADO\n{'=' * 60}")
    print(resultado.pydantic)

    print(f"\nUso de tokens: {crew.usage_metrics}")


if __name__ == "__main__":
    main()
