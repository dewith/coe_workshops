import random
import time
from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Dict
from typing import List

# Variable que contiene las letras del alfabeto y el espacio
letters = "abcdefghijklmnopqrstuvwxyz "

# Clase para definir colores de texto en la consola
class color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"

# Clase para representar un candidato en la población
@dataclass
class Candidate:
    text: str  # Texto del candidato
    fitness: int = -1  # Valor de fitness del candidato (inicialmente -1)
    in_focus: bool = False  # Indica si el candidato está enfocado (resaltado)

    # Método para obtener la representación en cadena del candidato
    def display_str(self, target_str: str) -> str: 
        prefix = "➤ " if self.in_focus else "  "  # Prefijo para indicar si está enfocado
        if self.fitness < 0:
            return prefix + self.text
        out = prefix
        for char, target_char in zip(self.text, target_str):
            if char != target_char:
                out += color.RED + char  # Resalta en rojo los caracteres diferentes
            else:
                out += color.GREEN + char  # Resalta en verde los caracteres iguales
        return out + color.END

    # Método para calcular el fitness del candidato en comparación con la cadena objetivo
    def set_fitness(self, target_str):
        self.fitness = sum(
            int(char == target_char) for char, target_char in zip(self.text, target_str)
        )

# Función para restablecer el enfoque de todos los candidatos en la población
def reset_focus(population: List[Candidate]) -> None:
    for candidate in population:
        candidate.in_focus = False

# Función para generar una población inicial con candidatos aleatorios
def seed_population(
    population: List[Candidate], population_size: int, target_str_len: int
) -> Iterable[str]: 
    """Genera una población con candidatos aleatorios y yield después de cada uno."""
    while len(population) < population_size:
        reset_focus(population)
        population.append(
            Candidate(
                text="".join(random.choice(letters) for _ in range(target_str_len)), 
                in_focus=True)
        )
        yield "Generando la población"

# Función para ordenar la población por fitness
def order_by_fitness(
    population: List[Candidate],
    target_str: str,
) -> Iterable[str]:
    for candidate in population:
        if candidate.fitness >= 0:
            continue
        reset_focus(population)
        candidate.set_fitness(target_str)  # Calcula el fitness del candidato
        candidate.in_focus = True
        yield "Calculando fitness"

    reset_focus(population)
    made_swap = True
    evens = True
    while made_swap:
        evens = not evens
        made_swap = False
        for i in range(int(evens), len(population), 2):
            if i + 1 >= len(population):
                continue
            candidate_a, candidate_b = population[i: i + 2]
            if candidate_a.fitness >= candidate_b.fitness:
                continue

            # Necesita intercambiar
            made_swap = True
            population[i] = candidate_b
            population[i + 1] = candidate_a

        yield "Ordenando por fitness"

# Función para eliminar los candidatos no aptos de la población
def remove_unfit(population: List[Candidate], num_fit_to_keep: int):
    while len(population) > num_fit_to_keep:
        population.pop()  # Elimina el último candidato de la población
        population[-1].in_focus = True
        yield "Eliminando candidatos no aptos"
    reset_focus(population)

# Función para generar un nuevo candidato a partir de dos padres
def breed(parent_a: Candidate, parent_b: Candidate, mutation_prob: float) -> Candidate:
    text = ""
    for char_a, char_b in zip(parent_a.text, parent_b.text):
        if random.random() < mutation_prob:
            text += random.choice(letters)  # Aplica una mutación aleatoria
        elif random.random() < 0.5:
            text += char_a  # Hereda el carácter del padre A
        else:
            text += char_b  # Hereda el carácter del padre B
    return Candidate(text=text)

# Función para generar nuevos candidatos mediante reproducción
def breed_new(population: List[Candidate], population_size: int, mutation_prob: float):
    num_fit = len(population)
    while len(population) < population_size:
        i = random.randint(0, num_fit - 1)
        j = (i + random.randint(1, num_fit - 1)) % num_fit

        parent_a = population[i]
        parent_b = population[j]
        reset_focus(population)
        parent_a.in_focus = True
        parent_b.in_focus = True
        child = breed(parent_a, parent_b, mutation_prob=mutation_prob)  # Genera un nuevo candidato
        child.in_focus = True
        population.append(child)
        yield "Generando nuevos candidatos"

# Función para mostrar la población en la consola
def display(
    *,
    population: List[Candidate],
    label: str,
    population_size: int,
    num_columns: int,
    column_width: int,
    target_str: str,
) -> None:  
    print("\n\n")
    print(
        color.BOLD
        + color.CYAN
        + label.center(column_width * num_columns)
        + color.END
        + "\n"
    )
    num_rows = population_size // num_columns
    cells = [["" for _ in range(num_columns)] for _ in range(num_rows)]

    for i in range(population_size):
        row_idx = i % num_rows
        col_idx = i // num_rows

        if i >= len(population):
            cells[row_idx][col_idx] = " " * column_width
            continue

        padding = column_width - len(target_str) - 2
        cells[row_idx][col_idx] = population[i].display_str(target_str) + " " * padding

    for row in cells:
        print("   " + "".join(row))

    print("\n")

# Función principal del programa
def main(target_str: str, population_size: int = 90, num_fit_to_keep: int = 12, 
         num_columns: int = 6, mutation_prob: float = 0.2,):  
    population: List[Candidate] = []
    column_width = len(target_str) + 6

    while True:
        for label in chain(
            seed_population(
                population,
                population_size=population_size,
                target_str_len=len(target_str),
            ),
            order_by_fitness(
                population,
                target_str=target_str
            ),
            remove_unfit(
                population,
                num_fit_to_keep=num_fit_to_keep
            ),
            breed_new(
                population,
                population_size=population_size,
                mutation_prob=mutation_prob
            ),
        ):
            time.sleep(0.011)
            print("\033[H\033[J", end="")
            display(
                population=population,
                label=label,
                population_size=population_size,
                num_columns=num_columns,
                column_width=column_width,
                target_str=target_str,
            )
            
        goal = num_fit_to_keep // 2
        if len(population) >= goal and all(candidate.text == target_str for candidate in population[:goal]):
            break

# Punto de entrada del programa
if __name__ == "__main__":
    target_str = input("Escribe una frase corta o da Enter: ")
    if not target_str.strip():
        target_str = "lisan al gaib"
        
    start = time.time()
    main(target_str=target_str.lower())
    print(f"{color.BLUE}Tiempo de ejecución: {color.BOLD}{time.time() - start:.0f} segundos{color.END}")