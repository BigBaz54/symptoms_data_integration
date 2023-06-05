import tkinter as tk
import interface

def update_results():
    # update the labels with the results of the functions
    input_value = input_field.get()
    print(input_value)

    symptoms_list = input_value.strip().replace("'", "").split(";")

    diseases = interface.getDiseaseHpo(symptoms_list)
    drug_from_stitch = interface.getMedicamentSiderStitch(symptoms_list)
    drug_from_drugbank = interface.getMedicamentDrugbank(symptoms_list)

    indications = ""
    indications+=("\nIndications for these symptoms: " + str(len(drug_from_stitch['indication'])+len(drug_from_drugbank['indication'])) + " hits" + "\n")
    indications+=('\n\tSTITCH: ' + str(len(drug_from_stitch['indication'])) + " hits" + "\n")
    for drug in drug_from_stitch['indication']:
        indications+=('\t\t' + drug + "\n")
    indications+=('\n\tDRUGBANK: ' + str(len(drug_from_drugbank['indication'])) + " hits" + "\n")
    for drug in drug_from_drugbank['indication']:
        indications+=('\t\t' + drug + "\n")

    side_effects = ""
    side_effects+=("\nThese symptoms are side effects of: " + str(len(drug_from_stitch['side_effect'])+len(drug_from_drugbank['side_effect'])) + " hits" + "\n")
    side_effects+=('\n\tSTITCH: ' + str(len(drug_from_stitch['side_effect'])) + " hits" + "\n")
    for drug in drug_from_stitch['side_effect']:
        side_effects+=('\t\t' + drug + "\n")
    side_effects+=('\n\tDRUGBANK: ' + str(len(drug_from_drugbank['side_effect'])) + " hits" + "\n")
    for drug in drug_from_drugbank['side_effect']:
        side_effects+=('\t\t' + drug + "\n")

    diseases_list = ""
    diseases_list+=("\nThese symptoms may be caused by the following diseases: " + str(len(diseases)) + " hits" + "\n")
    diseases_list+=('\n\tHPO -> OMIM:' + "\n")
    for disease in diseases:
        diseases_list+=('\t\t' + "OMIM_ID :" + disease["OMIM_id"] + "\n")
        diseases_list+=('\t\t' + "Preferred label: " + (disease["preferred_label"][0].replace('\"', '') if len(disease["preferred_label"]) > 0 else "No preferred label") + "\n")
        for syn in (disease["synonyms"][0] if len(disease["synonyms"]) > 0 else "No synonyms").split("|"):
            diseases_list+=('\t\t' + "Synonym: " + syn.replace('\"', '') + '\n')
        diseases_list+=("               ____" + '\n')

        

    result_1_text.delete("1.0", "end")
    result_1_text.insert("end", indications)

    result_2_text.delete("1.0", "end")
    result_2_text.insert("end", side_effects)

    result_3_text.delete("1.0", "end")
    result_3_text.insert("end", diseases_list)

# create the tkinter app window
window = tk.Tk()
window.title("Function App")

# set the window size
window.geometry("600x1200")

# create the input field
font = ('Arial', 10, 'bold')
input_label = tk.Label(window, text="Enter symptoms separated by ';':")
input_label.grid(row=0, column=0, padx=10, pady=10)
input_field = tk.Entry(window)
input_field.grid(row=0, column=1, padx=10, pady=10)

# create the results frames and text widgets with scrollbars
result_1_frame = tk.Frame(window)
result_1_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
result_1_scrollbar = tk.Scrollbar(result_1_frame)
result_1_scrollbar.pack(side="right", fill="y")
result_1_text = tk.Text(result_1_frame, height=5, yscrollcommand=result_1_scrollbar.set, width=45, font=font)
result_1_text.pack(side="left", fill="both")
result_1_scrollbar.config(command=result_1_text.yview)

result_2_frame = tk.Frame(window)
result_2_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
result_2_scrollbar = tk.Scrollbar(result_2_frame)
result_2_scrollbar.pack(side="right", fill="y")
result_2_text = tk.Text(result_2_frame, height=5, yscrollcommand=result_2_scrollbar.set, width=50, font=font)
result_2_text.pack(side="left", fill="both")
result_2_scrollbar.config(command=result_2_text.yview)

result_3_frame = tk.Frame(window)
result_3_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
result_3_scrollbar = tk.Scrollbar(result_3_frame)
result_3_scrollbar.pack(side="right", fill="y")
result_3_scrollbar2 = tk.Scrollbar(result_3_frame, orient=tk.HORIZONTAL)
result_3_scrollbar2.pack(side=tk.BOTTOM, fill=tk.X)
result_3_text = tk.Text(result_3_frame, height=5, yscrollcommand=result_3_scrollbar.set, xscrollcommand=result_3_scrollbar2.set, font=font)
result_3_text.configure(width=100, height=40)
result_3_text.pack(side="left")
result_3_scrollbar.config(command=result_3_text.yview)

# create the update button
update_button = tk.Button(window, text="Update Results", command=update_results)
update_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# run the app
window.mainloop()