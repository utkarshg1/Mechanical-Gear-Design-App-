# import all classes / functions from the tkinter
from tkinter import *
from sympy import symbols, diff, lambdify, pi
import pandas as pd


def show():
    label.config(text=clicked.get())


def clear_all():
    # whole content of entry boxes is deleted
    P.delete(0, END)
    Np.delete(0, END)
    g.delete(0, END)
    Sut.delete(0, END)
    Ep.delete(0, END)
    Eg.delete(0, END)
    Grade.delete(0, END)
    Cs.delete(0, END)
    fs.delete(0, END)
    m.delete(0, END)
    bx.delete(0, END)
    vel.delete(0, END)
    ptot.delete(0, END)
    fs_act.delete(0, END)
    BHNa.delete(0, END)
    zg.delete(0, END)
    zp.delete(0, END)

    # set focus on the principle_field entry box
    P.focus_set()


def Buckingham(mx):
    P1 = float(P.get())
    Np1 = int(Np.get())
    g1 = float(g.get())
    Sut1 = float(Sut.get())
    Ep1 = float(Ep.get())
    Eg1 = float(Eg.get())
    Grade1 = int(Grade.get())
    zp1 = int(zp.get())
    Cs1 = float(Cs.get())

    zg1 = g1 * zp1
    P1 = P1 * (10 ** 3)
    Ep1 = Ep1 * (10 ** 3)
    Eg1 = Eg1 * (10 ** 3)

    E = pd.read_csv("D:\Gear Tkinter\Gear Design Data\Gear Error.csv")
    b0 = float(E[E.Grade == Grade1]["b0"])
    b1 = float(E[E.Grade == Grade1]["b1"])

    # for Pinion
    dp = mx * zp1
    phip = mx + 0.25 * (dp ** 0.5)
    ep = b0 + b1 * phip

    # for gear
    dg = mx * zg1
    phig = mx + 0.25 * (dg ** 0.5)
    eg = b0 + b1 * phig

    # total
    e = (ep + eg) * (10 ** -3)

    k = 0.111  # Constant for 20 degree full depth Gear
    C = k / ((1 / Ep1) + (1 / Eg1))  # Deformation Factor in N/mm^2
    b = 10 * mx  # Face width of gears

    v = pi * dp * Np1 / 60000
    Pt = P1 / v
    a = 21 * v
    d = C * e * b + Pt
    Pd = (a * d) / (a + (d ** 0.5))
    Ptotal = Pt * Cs1 + Pd

    L = pd.read_csv("D:/Gear Tkinter/Gear Design Data/Lewis Form Factor.csv")
    Y = float(L[L["Z"] == str(zp1)]["Y"])

    Sb = mx * b * (Sut1 / 3) * Y

    fs_a = Sb / Ptotal

    return Ptotal, fs_a


def solve_m():
    m.delete(0, END)
    bx.delete(0, END)
    vel.delete(0, END)
    ptot.delete(0, END)
    fs_act.delete(0, END)
    BHNa.delete(0, END)
    zg.delete(0, END)

    P1 = float(P.get())
    Np1 = int(Np.get())
    g1 = float(g.get())
    Sut1 = float(Sut.get())
    Cs1 = float(Cs.get())
    fs1 = float(fs.get())
    zp1 = int(zp.get())

    L = pd.read_csv("D:/Gear Tkinter/Gear Design Data/Lewis Form Factor.csv")
    Y = float(L[L["Z"] == str(zp1)]["Y"])
    P1 = P1 * (10 ** 3)

    from sympy import pi, diff, lambdify, symbols
    m_x = symbols('m_x', real=True)
    dp = m_x * zp1
    v = pi * m_x * zp1 * Np1 / 60000
    Cv = 3 / (3 + v)  # Change if velocity is higher
    L = (P1 / v) * (Cs1 / Cv) * fs1
    b = 10 * m_x
    sigmab = Sut1 / 3
    R = m_x * b * sigmab * Y
    f = L - R
    f_dm = diff(f, m_x)

    f_l = lambdify(m_x, f, 'numpy')
    f_dm_l = lambdify(m_x, f_dm, 'numpy')
    v_l = lambdify(m_x, v, 'numpy')

    m0 = 4

    f0 = f_l(m0)
    mn = m0

    while not abs(f0) < (10 * (10 ** -10)):
        fx = f_l(mn)
        fdx = f_dm_l(mn)
        mn = m0 - fx / fdx
        m0 = mn
        f0 = fx

    m_list = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7, 0.75, 0.8, 0.9,
              1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.5, 4, 4.5, 5, 5.5, 6, 7, 8, 9, 10, 11,
              12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40, 45, 50]

    if mn > 50:
        mf = mn
    else:
        for n in range(len(m_list)):
            m_diff = m_list[n] - mn
            if m_diff >= 0:
                ind = n
                break
        mf = m_list[ind]

    Ptotal, fs_a = Buckingham(mf)
    while fs_a < fs1:
        if mf < 50:
            mf = m_list[ind + 1]
            ind = ind + 1
            Ptotal, fs_a = Buckingham(mf)
        else:
            mf = mf + 1
            Ptotal, fs_a = Buckingham(mf)

    b = 10 * mf
    dp = mf * zp1
    zg1 = g1 * zp1
    Q = (2 * zg1) / (zp1 + zg1)
    k = Ptotal * fs1 / (b * Q * dp)
    BHN = 100 * (k / 0.16) ** 0.5

    m.insert(10, mf)
    bx.insert(10, 10 * mf)
    vel.insert(10, float(v_l(mf)))
    ptot.insert(10, float(Ptotal))
    fs_act.insert(10, float(fs_a))
    BHNa.insert(10, float(BHN))
    zg.insert(10, zg1)


# Driver code
if __name__ == "__main__":
    # Create a GUI window
    root = Tk()

    # Set the background colour of GUI window
    root.configure(background='light blue')

    # Set the configuration of GUI window
    root.geometry("500x800")

    # Dropdown menu options
    #options = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 26, 28, 30, 34, 38, 43, 50, 60, 75, 100, 150, 300, 400,
    #           "Rack"]

    # datatype of menu text
    #clicked = StringVar()

    # initial menu text
    #clicked.set(18)

    # Create Dropdown menu
    #drop = OptionMenu(root, clicked, *options)
    #drop.pack()

    # set the name of tkinter GUI window
    root.title("Spur Gear(20 degree full depth involute) Design Calculator")

    # Create a Power : label
    label1 = Label(root, text="Power in kW(Kilo Watts) : ",
                   fg='black', bg='pink')

    # Create a RPM : label
    label2 = Label(root, text="Pinion Rotation speed in RPM(Revolutions per Minute) : ",
                   fg='black', bg='pink')

    # Create a Gear Ratio : label
    label3 = Label(root, text="Gear Ratio : ",
                   fg='black', bg='pink')

    # Create a Utimate tensile strength : label
    label4 = Label(root, text="Ultimate tensile strength in MPa(Mega Pascals) : ",
                   fg='black', bg='pink')

    # Create a Ep : label
    label5 = Label(root, text="Young's Modulus of Pinion in GPa  : ",
                   fg='black', bg='pink')

    # Create a Eg : label
    label6 = Label(root, text="Young's Modulus of Gear in GPa  : ",
                   fg='black', bg='pink')

    # Create a Grade : label
    label7 = Label(root, text="Grade of gear from 1 to 12  : ",
                   fg='black', bg='pink')

    # Create a Cs : label
    label8 = Label(root, text="Service Factor  : ",
                   fg='black', bg='pink')

    # Create a fos : label
    label9 = Label(root, text="Factor of Safety  : ",
                   fg='black', bg='pink')

    # Create a zp : label
    label10 = Label(root, text="Number of teeth on Pinion  : ",
                    fg='black', bg='pink')

    # Create module : label
    label11 = Label(root, text="Module of gear in mm  : ",
                    fg='black', bg='pink')

    # Create face width : label
    label12 = Label(root, text="Face width of gear in mm  : ",
                    fg='black', bg='pink')

    # Create velocity : label
    label13 = Label(root, text="Velocity of gear in m/sec  : ",
                    fg='black', bg='pink')

    # Create Total Load : label
    label14 = Label(root, text="Total load on pinion with Buckingham's equation  : ",
                    fg='black', bg='pink')

    # Create fs_a : label
    label15 = Label(root, text="Actual Factor of safety in strength  : ",
                    fg='black', bg='pink')

    # Create BHN : label
    label16 = Label(root, text="Brinnel's Hardness Number for pinion is  : ",
                    fg='black', bg='pink')

    # Create zg : label
    label17 = Label(root, text="Number of teeth on gear is  : ",
                    fg='black', bg='pink')

    # grid method is used for placing
    # the widgets at respective positions
    # in table like structure .

    # padx keyword argument used to set padding along x-axis .
    # pady keyword argument used to set padding along y-axis .
    label1.grid(row=1, column=1, padx=10, pady=10)
    label2.grid(row=2, column=1, padx=10, pady=10)
    label3.grid(row=3, column=1, padx=10, pady=10)
    label4.grid(row=4, column=1, padx=10, pady=10)
    label5.grid(row=5, column=1, padx=10, pady=10)
    label6.grid(row=6, column=1, padx=10, pady=10)
    label7.grid(row=7, column=1, padx=10, pady=10)
    label8.grid(row=8, column=1, padx=10, pady=10)
    label9.grid(row=9, column=1, padx=10, pady=10)
    label10.grid(row=10, column=1, padx=10, pady=10)
    label11.grid(row=12, column=1, padx=10, pady=10)
    label12.grid(row=13, column=1, padx=10, pady=10)
    label13.grid(row=14, column=1, padx=10, pady=10)
    label14.grid(row=15, column=1, padx=10, pady=10)
    label15.grid(row=16, column=1, padx=10, pady=10)
    label16.grid(row=17, column=1, padx=10, pady=10)
    label17.grid(row=18, column=1, padx=10, pady=10)

    # Create a entry box
    # for filling or typing the information.
    P = Entry(root)
    Np = Entry(root)
    g = Entry(root)
    Sut = Entry(root)
    Ep = Entry(root)
    Eg = Entry(root)
    Grade = Entry(root)
    Cs = Entry(root)
    fs = Entry(root)
    zp = Entry(root)
    m = Entry(root)
    bx = Entry(root)
    vel = Entry(root)
    ptot = Entry(root)
    fs_act = Entry(root)
    BHNa = Entry(root)
    zg = Entry(root)

    # grid method is used for placing
    # the widgets at respective positions
    # in table like structure .

    # padx keyword argument used to set padding along x-axis .
    # pady keyword argument used to set padding along y-axis .
    P.grid(row=1, column=2, padx=10, pady=10)
    Np.grid(row=2, column=2, padx=10, pady=10)
    g.grid(row=3, column=2, padx=10, pady=10)
    Sut.grid(row=4, column=2, padx=10, pady=10)
    Ep.grid(row=5, column=2, padx=10, pady=10)
    Eg.grid(row=6, column=2, padx=10, pady=10)
    Grade.grid(row=7, column=2, padx=10, pady=10)
    Cs.grid(row=8, column=2, padx=10, pady=10)
    fs.grid(row=9, column=2, padx=10, pady=10)
    zp.grid(row=10, column=2, padx=10, pady=10)
    m.grid(row=12, column=2, padx=10, pady=10)
    bx.grid(row=13, column=2, padx=10, pady=10)
    vel.grid(row=14, column=2, padx=10, pady=10)
    ptot.grid(row=15, column=2, padx=10, pady=10)
    fs_act.grid(row=16, column=2, padx=10, pady=10)
    BHNa.grid(row=17, column=2, padx=10, pady=10)
    zg.grid(row=18, column=2, padx=10, pady=10)

    # Create a Submit Button and attached
    # to calculate_ci function
    button1 = Button(root, text="Calculate", bg="blue",
                     fg="white", command=solve_m)

    # Create a Clear Button and attached
    # to clear_all function
    button2 = Button(root, text="Clear", bg="blue",
                     fg="white", command=clear_all)

    button1.grid(row=11, column=1, pady=10)
    button2.grid(row=11, column=2, pady=10)

    # Start the GUI
    root.mainloop()
