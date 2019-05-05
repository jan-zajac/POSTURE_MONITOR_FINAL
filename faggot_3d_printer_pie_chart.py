import matplotlib.pyplot as plt

# Data to plot
labels = 'Purchased parts', 'Laser Cutting', '3D printed'
sizes = [92.00, 7.00, 7.41]
colors = ['gold', 'yellowgreen', 'lightcoral']
explode = (0.1, 0, 0)  # explode 1st slice


def autopct_format(values):
    def my_format(pct):
        total = sum(values)
        val = float(round(pct*total/100.00, 4))
        val = format(val, '.2f')
        return '{v:s}'.format(v= str('£' + str(val)))
    return my_format
# Plot
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct = autopct_format(sizes), shadow=True, startangle=140)
#plt.title('Total cost of printer: £106.41', loc = 'right')
plt.title("Total cost of printer: " + r"$\bf{" + '£106.41' + "}$",loc = 'right')
plt.axis('equal')
plt.show()