import json
import os
import subprocess
import sys
from typing import Dict, List, Set


class DependencyVisualizer:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.package_name = self.config["package_name"]
        self.plantuml_path = self.config["plantuml_path"]
        self.repo_url = self.config["repo_url"]

    @staticmethod
    def load_config(config_path: str) -> Dict:
        """Загружает конфигурационный файл JSON."""
        with open(config_path, "r") as file:
            return json.load(file)

    def get_dependencies(self, package_name: str) -> Dict[str, Set[str]]:
        """
        Получает зависимости пакета, включая транзитивные.
        Использует `pip show` для анализа зависимостей.
        """
        dependencies = {}
        visited = set()

        def fetch_deps(pkg: str):
            if pkg in visited:
                return
            visited.add(pkg)
            result = subprocess.run(
                ["python3", "-m", "pip", "show", pkg],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print(f"Ошибка: не удалось получить информацию о пакете {pkg}")
                return
            deps = set()
            for line in result.stdout.splitlines():
                if line.startswith("Requires:"):
                    deps = set(line.split(":")[1].strip().split(", "))
                    break
            dependencies[pkg] = deps
            for dep in deps:
                if dep:
                    fetch_deps(dep)

        fetch_deps(package_name)
        return dependencies

    def generate_plantuml(self, dependencies: Dict[str, Set[str]]) -> str:
        """
        Генерирует текст PlantUML для графа зависимостей.
        """
        lines = ["@startuml", "digraph dependencies {"]
        for pkg, deps in dependencies.items():
            for dep in deps:
                if dep:
                    lines.append(f'    "{pkg}" -> "{dep}";')
        lines.append("}")
        lines.append("@enduml")
        return "\n".join(lines)

    def visualize(self, plantuml_code: str):
        """
        Визуализирует граф с помощью PlantUML.
        """
        with open("dependencies.puml", "w") as file:
            file.write(plantuml_code)

        # Генерация изображения
        subprocess.run(["java", "-jar", self.plantuml_path, "dependencies.puml"])

    def run(self):
        """
        Основной метод запуска визуализатора.
        """
        print(f"Сбор зависимостей для пакета {self.package_name}...")
        dependencies = self.get_dependencies(self.package_name)
        print("Генерация PlantUML...")
        plantuml_code = self.generate_plantuml(dependencies)
        print("Визуализация графа...")
        self.visualize(plantuml_code)
        print("Граф зависимостей успешно создан!")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python visualizer.py <путь_к_конфигурации>")
        sys.exit(1)

    config_path = sys.argv[1]
    visualizer = DependencyVisualizer(config_path)
    visualizer.run()