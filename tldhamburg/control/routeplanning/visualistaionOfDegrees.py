import numpy as np
import matplotlib.pyplot as plt

dic = {
"7038": [
        [
            0.9604373087002828,
            0.278496276557798,
            1.288568239167253,
            73.82952171888766
        ],
        [
            10.02994,
            53.606837
        ],
        [
            -0.9694705364119203,
            -0.24520782823797302,
            4.464654920732215,
            255.80588394027103
        ]
    ]
}
degin = 268.33157247267326
degOut = 88.53253644463626
priIn,priOut = 268.33157247267326,88.50133540391151
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


plt.quiver(*origin,-0.9995955084374588, -0.028439752313588623,color="purple")

plt.quiver(*origin,0.9996720288464607, 0.025609270626103048,color="pink")



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
plt.savefig("6608.pdf")