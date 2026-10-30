import tkinter as tk

ventana = tk.Tk()
ventana.title("Primer experimento con Canvas")

canvas = tk.Canvas(
    ventana, width=520, height=280,
    bg="#eef5ff", highlightthickness=0
)
canvas.pack(padx=16, pady=16)

# Un pequeño plano: una sala y una puerta.
canvas.create_text(260, 25, text="Haz clic dentro de la sala")
canvas.create_rectangle(40, 60, 480, 230, fill="white", outline="#345678", width=3)
canvas.create_rectangle(450, 120, 480, 175, fill="#a7e3bc", outline="#345678")
canvas.create_text(425, 147, text="Salida")

# Guardamos el ID del dibujo para poder moverlo después.
persona = canvas.create_oval(90, 120, 110, 140, fill="#2563eb", outline="")
estado = canvas.create_text(260, 255, text="El punto azul representa una persona")

def mover_persona(evento):
    x, y = evento.x, evento.y
    if not (50 <= x <= 470 and 70 <= y <= 220):
        return
    canvas.coords(persona, x - 10, y - 10, x + 10, y + 10)
    canvas.itemconfigure(estado, text=f"Persona en x={x}, y={y}")

canvas.bind("<Button-1>", mover_persona)
ventana.mainloop()