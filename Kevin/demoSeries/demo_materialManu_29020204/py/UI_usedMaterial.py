import Rhino
import Eto.Forms as forms
import Eto.Drawing as drawing
import webbrowser
import scriptcontext as sc

if winHeight is None:
    winHeight = 800
if rowNum is None:
    rowNum = 4

def create_label_with_font(text, font_size, font_family="Arial"):
    label = forms.Label(Text=text)
    label.Font = drawing.Font(font_family, font_size)
    return label

# Assume 'selectedIndices' is a global list defined outside this class 
# to store the indices of selected items. This is a simplification for demonstration.

selectedIndices = []  # This will be used to store the indices of selected items.
selectedBool = []

class TestWindow(forms.Form):  # Use Dialog[bool] for a modal dialog
    def __init__(self):
        super(TestWindow, self).__init__()
        self.Title = "Image Viewer"
#        self.MinimumSize = drawing.Size(100, 50)
        
        self.Location = drawing.Point(100, 100)


        self.checkBoxes = []

        self.layout = forms.DynamicLayout()
        self.layout.Height = winHeight

        self.scrollable = forms.Scrollable()
        self.imageLayout = forms.DynamicLayout()
        self.imageLayout.Padding = drawing.Padding(0, 10, 10, 60)
        self.scrollable.Content = self.imageLayout
        self.layout.AddRow(self.scrollable)

        self.Content = self.layout

        self.imagePaths = imagePaths
        self.urlList = urlList
        self.dataList = dataList
        self.populate_images()


    def populate_images(self):
        images_per_row = rowNum
        row = []
        count = 0
        
        for path, data, urrl in zip(self.imagePaths, self.dataList, self.urlList):
            try:
                unitLayout = forms.StackLayout()
                unitLayout.Orientation = forms.Orientation.Vertical
                unitLayout.Spacing = 5
                unitLayout.Padding = drawing.Padding(10)
    
                image = drawing.Bitmap(path)
                imageView = forms.ImageView()
                imageView.Image = image
                imageView.Size = drawing.Size(250, 250)  # Fixed size for the image
    
                # Create a horizontal StackLayout for descriptions
                descriptionsLayout = forms.StackLayout()
                descriptionsLayout.Spacing = 3
                
                descriptions = data
                
                desired_font_size = 10
                
                for desc in descriptions:
                    # Create and add labels with the desired font size to the layout.
                    descriptionsLayout.Items.Add(create_label_with_font(desc, desired_font_size))
                
                # Encapsulate descriptionsLayout in a Scrollable for horizontal scrolling
                descriptionScrollable = forms.Scrollable()
                descriptionScrollable.Content = descriptionsLayout
                
                # Set the size of the Scrollable to match the imageView's size
                # Here, the height is arbitrary since it's a horizontal scroll
                descriptionScrollable.Width = imageView.Width
                
                link_button = forms.LinkButton(Text="Open Website")
                link_button.Click += lambda sender, e, url=urrl: webbrowser.open(url)
                
                
                # Checkbox and Label Pair
                checkBoxLabelLayout = forms.StackLayout()  # Horizontal layout for checkbox and label
                checkBoxLabelLayout.Orientation = forms.Orientation.Horizontal
                checkBoxLabelLayout.Spacing = 5
                
                checkBox = forms.CheckBox() #####################################
                checkBox.CheckedChanged += self.on_checked_changed
                self.checkBoxes.append(checkBox)
                
                checkBoxLabel = forms.Label(Text="Show in Rhino")  # Custom font label
                checkBoxLabel.Font = drawing.Font("Arial Bold", 13)  # Set the font here
                
                checkBoxLabelLayout.Items.Add(checkBox)
                checkBoxLabelLayout.Items.Add(checkBoxLabel)
                
                
                # Add the imageView, descriptionScrollable, and checkBox to the unitLayout
                unitLayout.Items.Add(imageView)
                unitLayout.Items.Add(descriptionScrollable)  # Add the scrollable descriptions
                unitLayout.Items.Add(link_button)
                unitLayout.Items.Add(checkBoxLabelLayout)
    
                row.append(unitLayout)
    
                count += 1
                if count == images_per_row:
                    self.imageLayout.AddRow(*row)
                    row = []
                    count = 0
    
            except Exception as e:
                forms.MessageBox.Show("Failed to load image: " + str(e))
    
        if row:
            self.imageLayout.AddRow(*row)
    
    
    def on_checked_changed(self, sender, e):
        # Update the stored state when a checkbox is changed
        states = [checkBox.Checked for checkBox in self.checkBoxes]
        sc.sticky['checkbox_states'] = states



imagePaths = [image[0] for image in imagePaths.Branches]
urlList = [urll[0] for urll in urlList.Branches]
dataList = [d for d in data.Branches]


def show_check_box_form():
    form = TestWindow()
    form.Show()

# A simple function to simulate a value listener that polls for checkbox state changes
def poll_checkbox_states():
    # Default to all False if not set
    return sc.sticky.get('checkbox_states', [False] * showNum)

# This would be your Grasshopper component's main run function
# Use a timer to periodically trigger this function
checkbox_states = poll_checkbox_states()


# Assuming 'showForm' is a boolean input to trigger the form display
if open:
    sc.sticky['checkbox_states'] = [False] * showNum
    show_check_box_form()