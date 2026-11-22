"""Herramientas del agente. Cada una es una función pequeña, con descripción y parámetros explícitos.
Todas operan DENTRO del directorio de trabajo (sandbox).

Adaptación EcoRecicla (Lab 10): `original` apunta al repositorio real para `ver_cambios`,
`ejecutar_pruebas` usa el mismo intérprete de Python y fuerza UTF-8 (necesario en Windows)."""
import ast
import pathlib
import re
import subprocess
import sys


class Herramientas:
    def __init__(self, raiz: str, original: str = "../trabajo_original"):
        self.raiz = pathlib.Path(raiz).resolve()
        self.original = original

    # --- utilidades ---
    def _ruta(self, ruta: str) -> pathlib.Path:
        p = (self.raiz / ruta).resolve()
        if self.raiz not in p.parents and p != self.raiz:
            raise PermissionError(f"Ruta fuera del sandbox: {ruta}")
        return p

    def catalogo(self) -> dict:
        """Descripción de las herramientas que se envía al modelo (como en un MCP server)."""
        return {
            "listar_archivos": "listar_archivos(carpeta='.'): lista los archivos .py y .md",
            "leer_archivo": "leer_archivo(ruta): devuelve el contenido con números de línea",
            "buscar": "buscar(patron): busca una expresión regular en los archivos .py",
            "mapa_repo": "mapa_repo(carpeta='.'): devuelve rutas y firmas de funciones, clases y métodos Python dentro del sandbox",
            "anotar": "anotar(texto): agrega una nota breve y persistente a notas.md dentro del sandbox",
            "leer_notas": "leer_notas(): devuelve el contenido persistente de notas.md",
            "ejecutar_pruebas": "ejecutar_pruebas(ruta=''): ejecuta pytest (toda la suite o solo la ruta indicada) y devuelve el resumen",
            "editar_archivo": "editar_archivo(ruta, antes, despues): reemplaza un fragmento exacto (una sola vez)",
            "ver_cambios": "ver_cambios(): muestra el diff respecto de la versión original",
            "ejecutar_comando": "ejecutar_comando(comando): ejecuta un comando de shell (sujeto a la política)",
        }

    # --- herramientas ---
    def listar_archivos(self, carpeta="."):
        base = self._ruta(carpeta)
        return "\n".join(sorted(p.relative_to(self.raiz).as_posix() for p in base.rglob("*")
                                if p.suffix in (".py", ".md") and "__pycache__" not in p.parts))

    def leer_archivo(self, ruta):
        lineas = self._ruta(ruta).read_text(encoding="utf-8").splitlines()
        return "\n".join(f"{i:3d}| {l}" for i, l in enumerate(lineas, 1))

    def buscar(self, patron):
        rx, hallazgos = re.compile(patron), []
        for p in sorted(self.raiz.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            for i, l in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if rx.search(l):
                    hallazgos.append(f"{p.relative_to(self.raiz).as_posix()}:{i}: {l.strip()}")
        return "\n".join(hallazgos) or "(sin resultados)"

    def mapa_repo(self, carpeta="."):
        base = self._ruta(carpeta)
        if not base.exists():
            return f"ERROR: carpeta inexistente: {carpeta}"
        if not base.is_dir():
            return f"ERROR: no es una carpeta: {carpeta}"

        bloques = []
        for p in sorted(base.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            try:
                arbol = ast.parse(p.read_text(encoding="utf-8"), filename=p.as_posix())
            except (SyntaxError, UnicodeDecodeError) as error:
                bloques.append(f"{p.relative_to(self.raiz).as_posix()}: ERROR {error}")
                continue

            firmas = []
            for nodo in arbol.body:
                if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    firmas.append(f"{nodo.name}{ast.unparse(nodo.args)}")
                elif isinstance(nodo, ast.ClassDef):
                    for miembro in nodo.body:
                        if isinstance(miembro, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            firmas.append(f"{nodo.name}.{miembro.name}{ast.unparse(miembro.args)}")
            if firmas:
                bloques.append(f"{p.relative_to(self.raiz).as_posix()}: " + "; ".join(firmas))
        return "\n".join(bloques) or "(sin módulos Python)"

    def anotar(self, texto):
        if not isinstance(texto, str) or not texto.strip():
            return "ERROR: la nota no puede estar vacía"
        notas = self.raiz / "notas.md"
        with notas.open("a", encoding="utf-8") as archivo:
            archivo.write(texto.strip() + "\n")
        return f"OK: nota agregada a notas.md ({len(texto)} caracteres)"

    def leer_notas(self):
        notas = self.raiz / "notas.md"
        if not notas.exists():
            return "(sin notas)"
        return notas.read_text(encoding="utf-8").strip() or "(sin notas)"

    def ejecutar_pruebas(self, ruta=""):
        cmd = [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"]
        if ruta:
            cmd.append(str(self._ruta(ruta).relative_to(self.raiz)))   # validada contra el sandbox
        r = subprocess.run(cmd, cwd=self.raiz, capture_output=True, text=True, timeout=120,
                           encoding="utf-8", errors="replace")
        salida = (r.stdout + r.stderr).strip().splitlines()
        fallos = [l for l in salida if l.startswith(("FAILED", "E "))][:6]
        return "\n".join(fallos + salida[-1:])

    def editar_archivo(self, ruta, antes, despues):
        p = self._ruta(ruta)
        texto = p.read_text(encoding="utf-8")
        if texto.count(antes) != 1:
            return f"ERROR: el fragmento aparece {texto.count(antes)} veces; debe aparecer exactamente 1"
        p.write_text(texto.replace(antes, despues), encoding="utf-8")
        return f"OK: {ruta} modificado"

    def ver_cambios(self, original=None):
        import difflib
        base, salida = self._ruta_libre(original or self.original), []
        for p in sorted(self.raiz.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            rel = p.relative_to(self.raiz); q = base / rel
            a = q.read_text(encoding="utf-8").splitlines() if q.exists() else []
            salida += difflib.unified_diff(a, p.read_text(encoding="utf-8").splitlines(),
                                           f"a/{rel.as_posix()}", f"b/{rel.as_posix()}", lineterm="", n=1)
        return "\n".join(salida) or "(sin cambios)"

    def _ruta_libre(self, ruta):
        return (self.raiz / ruta).resolve()

    def ejecutar_comando(self, comando):
        r = subprocess.run(comando, shell=True, cwd=self.raiz, capture_output=True, text=True, timeout=60,
                           encoding="utf-8", errors="replace")
        return (r.stdout + r.stderr).strip()[-2000:]
