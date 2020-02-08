import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import showinfo
from group import *
import os

root = Tk()
root.title("Group Sorter")

df = pd.DataFrame()
importFile = ''
exportFile = ''
cols = []
indexCol = IntVar()
seedCol = dict()
categoryList = dict()
categoryWeightsDict = dict()
quartileList = dict()
quartileWeightsDict = dict()

numOfTeamsEntry = Entry(root)
iterationsEntry = Entry(root)
topEntry = Entry(root)


def UploadAction():
    global importFile

    importFile = filedialog.askopenfilename()
    print('Selected:', importFile)
    Label(root, text=importFile).grid(row=0, column=2, columnspan=5)
    checkBoxes()


def ExportAction(_row):
    global exportFile

    exportFile = filedialog.asksaveasfilename(title="Select file", filetypes=(("Excel files", "*.xlsx"),
                                                                              ("All files", "*.*")))
    print('Selected:', exportFile)
    if(exportFile):
        Label(root, text=exportFile+'.xlsx').grid(row=_row -
                                                  1, column=2, columnspan=5)


def checkBoxes():
    global df
    global cols

    global indexCol
    global seedCol
    global categoryList
    global categoryWeightsDict
    global quartileList
    global quartileWeightsDict

    if importFile.endswith('.csv'):
        df = pd.read_csv(importFile)  # import csv file
    elif importFile.endswith('.xls') or importFile.endswith('.xlsx'):
        df = pd.read_excel(importFile)  # import excel file
    cols = list(df)
    row = 1
    prevRow = row

    Label(root, text='Index Var: ').grid(
        row=row, column=0, sticky=W)
    row += 1
    indexCol = IntVar()
    for idx, col in enumerate(cols):
        Radiobutton(root, text=col, variable=indexCol, value=idx).grid(
            row=row, column=0, sticky=W)
        row += 1

    row = prevRow
    Label(root, text='Seed Var: ').grid(
        row=row, column=1, sticky=W)
    row += 1
    for idx, col in enumerate(cols):
        seedCol[idx] = IntVar()
        Checkbutton(root, text=col, variable=seedCol[idx]).grid(
            row=row, column=1, sticky=W)
        row += 1

    row = prevRow
    Label(root, text='Categorical Vars: ').grid(
        row=row, column=2, sticky=W)
    Label(root, text='Assign Weights: ').grid(
        row=row, column=3, sticky=W)
    row += 1
    for idx, col in enumerate(cols):
        categoryList[idx] = IntVar()
        Checkbutton(root, text=col, variable=categoryList[idx]).grid(
            row=row, column=2, sticky=W)
        categoryWeightsDict[idx] = Entry(root)
        categoryWeightsDict[idx].grid(row=row, column=3, sticky=W)
        row += 1

    row = prevRow
    Label(root, text='Quartile Vars: ').grid(
        row=row, column=5, sticky=W)
    Label(root, text='Assign Weights: ').grid(
        row=row, column=6, sticky=W)
    row += 1
    for idx, col in enumerate(cols):
        quartileList[idx] = IntVar()
        Checkbutton(root, text=col, variable=quartileList[idx]).grid(
            row=row, column=5, sticky=W)
        quartileWeightsDict[idx] = Entry(root)
        quartileWeightsDict[idx].grid(row=row, column=6, sticky=E)
        row += 1

    row += 1
    Label(root, text='Number of Teams: ').grid(row=row, columnspan=3, sticky=W)
    row += 1
    numOfTeamsEntry.grid(row=row, column=0, columnspan=2, sticky=W)
    numOfTeams = numOfTeamsEntry.get()

    row += 1
    Label(root, text='Number of Iterations: ').grid(row=row, columnspan=2, sticky=W)
    row += 1
    iterationsEntry.grid(row=row, column=0, columnspan=2, sticky=W)
    iterations = iterationsEntry.get()

    row += 1
    Label(root, text='Generate Top ? Iterations: ').grid(row=row, columnspan=2, sticky=W)
    row += 1
    topEntry.grid(row=row, column=0, columnspan=2, sticky=W)
    top = topEntry.get()

    row += 1
    Button(root, text='Export results to...', command=lambda: ExportAction(row)).grid(
        row=row, sticky=W, pady=10, columnspan=2)

    row += 1
    Button(root, text='Generate', command=generate).grid(
        row=row, sticky=W, pady=10, columnspan=2)


###### Convert the Inputs and Pass to group.py ######


def generate():
    global indexCol
    global seedCol
    global categoryList
    global categoryWeightsDict
    global quartileList
    global quartileWeightsDict

    selectedIndexCol = [cols[indexCol.get()]]

    temp1 = [i.get() for i in seedCol.values()]
    selectedSeedCol = [col for col, idx in zip(cols, temp1) if idx == 1]

    temp1 = [i.get() for i in categoryList.values()]
    selectedCategoryCols = [col for col, idx in zip(cols, temp1) if idx == 1]

    temp2 = [1 if i.get() == '' else int(i.get())
             for i in categoryWeightsDict.values()]
    categoryWeights = [weight for weight, idx in zip(temp2, temp1) if idx == 1]

    temp1 = [i.get() for i in quartileList.values()]
    selectedQuartileCols = [col for col, idx in zip(cols, temp1) if idx == 1]

    temp2 = [1 if i.get() == '' else int(i.get())
             for i in quartileWeightsDict.values()]
    quartileWeights = [weight for weight, idx in zip(temp2, temp1) if idx == 1]

    numOfTeams = int(numOfTeamsEntry.get())
    iterations = int(iterationsEntry.get())
    selectTop = int(topEntry.get())
    if main(importFile, selectedIndexCol, selectedSeedCol, selectedCategoryCols, categoryWeights,
            selectedQuartileCols, quartileWeights, numOfTeams, iterations, selectTop, exportFile):
        showinfo("Results", "Done!")
    else:
        showinfo("Error", "Close your export files")


Button(root, text='Import Excel/CSV File to Start', command=lambda: UploadAction()).grid(
    padx=20, pady=20, columnspan=2)

mainloop()
