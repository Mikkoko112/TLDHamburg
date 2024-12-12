import numpy as np
import matplotlib.pyplot as plt


degin = 268.5348039106532
degOut = 88.77493001030624
priIn = 214.07015603762616
priOut= 82.56176244531581
# Parameter degin,degout,priIn,priOut
gradzahlen = [degin, degOut, priIn-60,priIn+60,priOut-60,priOut+60]  # Grad in Winkel
color = ["red","orange","blue","blue","black","black"]
radius = 1  # Radius des Kreises
origin = np.array([0, 0])  # Ursprung

# Kreis erstellen
winkel = np.linspace(0, 2 * np.pi, 100)
kreis_x = radius * np.cos(winkel)
kreis_y = radius * np.sin(winkel)

# Standardvektor
standardvektor = np.array([0, 1])

# Plot initialisieren
plt.figure(figsize=(8, 8))
plt.plot(kreis_x, kreis_y, label="Kreis")  # Kreis zeichnen
plt.scatter(*origin, color="black", label="Ursprung")  # Ursprung markieren

# Vektoren einzeichnen
for grad,c in zip(gradzahlen,color):
    rad = np.deg2rad(grad)  # Grad in Bogenmaß
    vektor = np.array([np.sin(rad), np.cos(rad)])  # Vektor berechnen
    plt.quiver(*origin, vektor[0], vektor[1], angles="xy", scale_units="xy", scale=1, color=c, alpha=0.7, label=f"Vektor {grad}°" if grad == gradzahlen[0] else "")

# Achsen und Anzeigeoptionen
plt.axhline(0, color='black', linewidth=0.5, linestyle='--')
plt.axvline(0, color='black', linewidth=0.5, linestyle='--')
plt.gca().set_aspect('equal', adjustable='box')
plt.xlim(-1.2, 1.2)
plt.ylim(-1.2, 1.2)
plt.title("Vektoren um einen Kreis")
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(alpha=0.3)
plt.savefig("16963-2.pdf")