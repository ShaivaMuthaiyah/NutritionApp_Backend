# importing modules 
from reportlab.pdfgen import canvas 
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import numpy as np
from matplotlib import pyplot as plt

import os


# data = {'basic_metrics': 
#                 {'bmi': 24.3, 
#                 'bmi_category': 'Normal weight', 
#                 'ideal_body_weight': 74.3, 
#                 'current_weight': 78.0, 
#                 'body_fat_percentage': 19.4,
#                 "ideal_body_fat_percentage": [7, 17]
#                 }, 

#             'caloric_needs':
#                 {'goal_caloric_needs': 2450, 
#                 'macronutrients':
#                 {'protein': 125, 'fat': 68, 'carbs': 334}
#                 }, 

#             'recommendations': 
#                 {'water_intake': 2.73, 
#                 'fiber_intake': 34.3, 
#                 'sugar_intake': 30
#                 }, 

#             'diet_details': 
#                 {'diet': 'vegan', 
#                 'allergies': ['None']
#                 }
#             }


def generateHealthReport(data, id):


    # initializing variables with values 

    reports_directory = "reports"

    fileName = f'{reports_directory}/nutrition_report_{id}.pdf'
    documentTitle = 'sample'
    title = 'Your Nutrition Report'
    subTitle = 'Here is an overview of your results and some suggestions'
    font = "Helvetica-Bold"

    # colour palette from lightest to darkest
    green_palette = {
        'green_0': (202/255, 210/255, 197/255),
        'green_1': (132/255, 169/255, 140/255),
        'green_2': (82/255, 121/255, 111/255),
        'green_3': (53/255, 79/255, 82/255),
        'green_4': (47/255, 62/255, 70/255)
    }



    user_id = id
    nutrition_chart = f'{reports_directory}/nutrition_{user_id}.jpg'
    weight_chart = f'{reports_directory}/weight_{user_id}.jpg'
    fiberwater_chart = f'{reports_directory}/fiber_water_{user_id}.jpg'
    fat_chart = f'{reports_directory}/fat_{user_id}.jpg'
    fat_types_chart = f'{reports_directory}/fat_types_{user_id}.jpg'





    # pie chart for the nutrition breakup
    # --------------------------------------------
    labels = ['carbs', 'protein', 'fat']
    pie_labels = [label.capitalize() for label in labels]
    pie_data = [data['caloric_needs']['macronutrients'][label] for label in labels]
    pie_colours = [green_palette[f'green_{i}'] for i in range(2, 5)]


    def func(pct, allvalues):
        absolute = int(pct / 100.*np.sum(allvalues))
        return "{:.1f}%\n({:d} g)".format(pct, absolute)

    plt.figure(figsize=(4, 4))

    plt.pie(pie_data, 
        labels=pie_labels,
        textprops={'color':"w"},
        colors=pie_colours,
        autopct=lambda pct: func(pct, pie_data),)

    plt.title('Macronutrient Breakdown')
    plt.legend()
    plt.savefig(nutrition_chart, dpi=100)
    # plt.show()
    # --------------------------------------------




    # pie chart for the nutrition breakup
    # --------------------------------------------
    labels = ['Unsaturated Fats', 'Saturated Fats', 'Trans Fats']
    pie_labels = [label.capitalize() for label in labels]
    pie_data = [89, 10, 1]
    pie_colours = [green_palette[f'green_{i}'] for i in range(1, 4)]


    def func(pct, allvalues):
        absolute = int(pct / 100.*np.sum(allvalues))
        return "{:.1f}%".format(pct, absolute)

    plt.figure(figsize=(4, 4))

    plt.pie(pie_data, 
        labels=pie_labels,
        textprops={'color':"w"},
        colors=pie_colours,
        autopct=lambda pct: func(pct, pie_data),)

    plt.title('Percentage of Calories from different Fats (Recommended)', fontsize=8)
    plt.legend()
    plt.savefig(fat_types_chart, dpi=100)
    # plt.show()
    # --------------------------------------------




    # bar chart for the weight comparison
    # --------------------------------------------

    bar_labels = np.array(['Ideal Weight', 'Current Weight'])
    bar_data = np.array([data['basic_metrics']['ideal_body_weight'], data['basic_metrics']['current_weight']])
    bar_color = [green_palette['green_0'], green_palette['green_1'] if data['basic_metrics']['ideal_body_weight'] < data['basic_metrics']['current_weight'] else green_palette['green_2']]

    plt.figure(figsize=(3, 3))
    plt.title('Ideal vs Current Weight (in Kg)')
    bars = plt.bar(
        bar_labels, 
        bar_data, 
        color=bar_color
    )

    # Display the values on the bars
    for bar in bars:
        value = bar.get_height()  # Get the height of the bar
        position = value - 1  # Position slightly inside the bar for tall bars
        color = 'black'  # Contrast text color for visibility
        
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # Center horizontally
            position if value > 10 else value + 0.5,  # Inside or above the bar based on its height
            f"{value:.1f}",  # Format the value
            va='center' if value > 10 else 'bottom',  # Adjust alignment
            ha='center',  # Center text
            fontsize=12,
            color=color
        )
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(weight_chart, dpi=100)
    # plt.show()

    # --------------------------------------------





    # bar chart for the fiber and sugar comparison
    # --------------------------------------------

    bar_labels = np.array(['Fiber', 'Sugar (Max)'])
    bar_data = np.array([data['recommendations']['fiber_intake'], data['recommendations']['sugar_intake']])
    bar_color = [green_palette['green_2'], green_palette['green_1']]

    # Create a horizontal bar chart
    plt.figure(figsize=(8, 4))
    plt.title('Fiber and Sugar Allowance (in g)', fontsize=16)

    bars = plt.barh(bar_labels, 
                    bar_data, 
                    color=bar_color,
                    )

    # Display the values on the bars
    for bar in bars:
        value = bar.get_width()
        position = value - 1  # Position inside the bar for labels on long bars
        color = 'white' if value > 3 else 'black'  # Contrast text color for visibility
        
        plt.text(
            position if value > 3 else value + 0.5,  # Inside or outside the bar based on its width
            bar.get_y() + bar.get_height() / 2,  # Center vertically
            f"{value:.1f}",  # Format the value
            va='center',
            ha='right' if value > 3 else 'left',  # Align text for readability
            fontsize=18,
            color=color
        )

    plt.grid(True, linestyle='--', alpha=0.7)
    # Save the chart
    plt.savefig(fiberwater_chart, dpi=100)
    # plt.show()

    # --------------------------------------------



    # area chart for the body fat percentage
    # --------------------------------------------

    # Extract relevant data
    ideal_range = data["basic_metrics"]["ideal_body_fat_percentage"]
    current_value = data["basic_metrics"]["body_fat_percentage"]

    # Define x-axis (dummy range for line representation)
    area_x = np.array(range(1, 3))  # Use a small range to represent the ideal range
    area_y_min = np.full_like(area_x, ideal_range[0])
    area_y_max = np.full_like(area_x, ideal_range[1])

    # Plotting
    plt.figure(figsize=(7, 4))

    # Plot the ideal range as a line chart
    plt.plot(area_x, area_y_min, label=f"Ideal Min: {ideal_range[0]}%", color=green_palette['green_2'], linestyle='--')
    plt.plot(area_x, area_y_max, label=f"Ideal Max: {ideal_range[1]}%", color=green_palette['green_1'], linestyle='--')

    # Add the current value as a dot
    plt.scatter([1.5], [current_value], color=green_palette['green_4'], label=f"Current: {current_value}%")

    # Customize the chart
    plt.title('Ideal Body Fat Percentage Range', fontsize=14)
    plt.ylabel('Body Fat Percentage (%)', fontsize=14)
    plt.ylim(0, 25)  # Adjust range to fit the data
    plt.xticks([])
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(fat_chart, dpi=100)

    # Display
    # plt.show()
    # --------------------------------------------





    # creating a pdf object 
    pdf = canvas.Canvas(fileName, pagesize=A4) 
    
    # setting the title of the document
    pdf.setFont(font, 24) 
    pdf.setTitle(documentTitle)
    
    # creating the title by setting it's font  
    pdf.drawCentredString(300, 770, title)


    # drawing a line
    pdf.line(30, 740, 550, 740)



    # creating the subtitle by setting it's font,  
    # colour and putting it on the canvas 
    pdf.setFillColor(colors.darkseagreen) 
    pdf.setFont(font, 10) 
    pdf.drawCentredString(290, 750, subTitle) 
    


    # report ID details 

    pdf.setFillColor(colors.black) 
    pdf.setFontSize(8)
    pdf.drawString(360, 820, "Report ID:")

    pdf.setFillColor(green_palette['green_2']) 
    pdf.drawString(400, 820, str(user_id))


    # weight related information
    # ---------------------------------------------
    pdf.setFillColor(colors.darkseagreen) 
    pdf.setFontSize(12)
    pdf.drawString(40, 700, 'Weight Metrics') 


    pdf.setFillColor(colors.black) 
    pdf.setFontSize(10)
    pdf.drawString(40, 675, 'Your BMI:') 
    pdf.drawString(190, 675, 'BMI Category:') 
    pdf.drawString(400, 675, 'Bodyfat Percentage:') 


    pdf.setFillColor(green_palette['green_2']) 
    pdf.setFontSize(10)
    pdf.drawString(90, 675, text=str(data['basic_metrics']['bmi'])) 
    pdf.drawString(260, 675, text=str(data['basic_metrics']['bmi_category'])) 
    pdf.drawString(500, 675, text=str(data['basic_metrics']['body_fat_percentage'])) 


    # ----------------------------------------------



    # nutritional related information
    # ---------------------------------------------

    pdf.setFillColor(colors.darkseagreen) 
    pdf.setFontSize(12)
    pdf.drawString(40, 450, 'Nutrition Suggestions') 

    pdf.setFillColor(colors.black) 
    pdf.setFontSize(10)
    pdf.drawString(40, 425, 'Daily Caloric Goal:') 


    pdf.setFillColor(green_palette['green_2']) 
    pdf.setFontSize(10)
    pdf.drawString(130, 425, text=f"{str(data['caloric_needs']['goal_caloric_needs'])} Kcal") 




    # miscellaneous related information
    # ---------------------------------------------


    pdf.setFillColor(colors.darkseagreen) 
    pdf.setFontSize(12)
    pdf.drawString(40, 210, 'Other Suggestions') 

    pdf.setFillColor(colors.black) 
    pdf.setFontSize(10)
    pdf.drawString(40, 185, 'Daily Water Intake:') 
    pdf.drawString(40, 155, 'Maximum Sodium Intake:')


    pdf.setFillColor(green_palette['green_2']) 
    pdf.setFontSize(10)
    pdf.drawString(132, 185, text=f"{str(data['recommendations']['water_intake'])} L") 
    pdf.drawString(162, 155, text='2000 mg') 


    # creating a multiline text using  
    # textline and for loop 



    # notes and exceptions information
    # ---------------------------------------------
    pdf.setFillColor(green_palette['green_2']) 
    pdf.setFontSize(8)
    pdf.drawString(40, 120, text='Note:') 
    pdf.drawString(40, 110, text='Source: https://my.clevelandclinic.org') 

    pdf.setFillColor(green_palette['green_4'])
    pdf.setFontSize(8)
    pdf.drawString(40, 95, text="- BMI doesn't distinguish between lean body mass and fat mass.")
    pdf.drawString(40, 85, text="- Same chart used for all genders despite body fat differences.")
    pdf.drawString(40, 75, text="- Charts not adjusted for increasing average adult heights.")
    pdf.drawString(40, 65, text="- Unsuitable for athletes, children, pregnant people, seniors, etc.")

    pdf.drawInlineImage(weight_chart, 40, 480, width=180, height=180)
    pdf.drawInlineImage(fat_chart, 270, 480, width=310, height=180) 
    pdf.drawInlineImage(nutrition_chart, 300, 200, width=250, height=250)
    pdf.drawInlineImage(fiberwater_chart, 40, 250, width=300, height=150)
    pdf.drawInlineImage(fat_types_chart, 300, 0, width=240, height=240)



    pdf.line(30, 25, 550, 25)

    # saving the pdf 
    pdf.save() 




def cleanupActivity(id):

    # cleanup activities
    # -----------------------------------------------
    user_id_str = str(id)
    reports_directory = "reports"

    # Loop through all files in the current directory
    for file_name in os.listdir("reports"):
        # Check if the file is a .jpg and contains the user_id
        if user_id_str in file_name:

            # Construct the full path to the file
            file_path = os.path.join(reports_directory, file_name)
            
            # Delete the file
            try:
                os.remove(file_path)
                print(f"Deleted: {file_name}")
            except Exception as e:
                print(f"Error deleting {file_name}: {e}")



def cleanupActivityFolder():

    # cleanup activities
    # -----------------------------------------------
    reports_directory = "reports"

    # Loop through all files in the current directory
    for file_name in os.listdir("reports"):

            # Construct the full path to the file
        file_path = os.path.join(reports_directory, file_name)
            
        # Delete the file
        try:
            os.remove(file_path)
            print(f"Deleted: {file_name}")
        except Exception as e:
            print(f"Error deleting {file_name}: {e}")