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

def create_white_image(width, height):
    """Create a white bitmap image of specified width and height."""
    white_image = drawing.Bitmap(width, height, drawing.PixelFormat.Format32bppRgb)
    with drawing.Graphics(white_image) as g:
        g.Clear(drawing.Colors.White)  # Fill the image with white color
    return white_image

# Assume 'selectedIndices' is a global list defined outside this class 
# to store the indices of selected items. This is a simplification for demonstration.

selectedIndices = []  # This will be used to store the indices of selected items.
selectedBool = []

class innerMaterialWindow(forms.Form):  # Use Dialog[bool] for a modal dialog
    def __init__(self):
        super(innerMaterialWindow, self).__init__()
        self.Title = "Image Viewer"
        
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
        self.usedDataList = usedDataList
        self.populate_images()

    def populate_images(self):
        images_per_row = rowNum
        row = []
        count = 0
        
        for path, data, urrl, usedData in zip(self.imagePaths, self.dataList, self.urlList, self.usedDataList):

            try:
                unitLayout = forms.StackLayout()
                unitLayout.Orientation = forms.Orientation.Vertical
                unitLayout.Spacing = 5
                unitLayout.Padding = drawing.Padding(10)
    
                imageView = forms.ImageView()
                imageView.Size = drawing.Size(250, 250)  # Fixed size for the image
                
                try:
                    image = drawing.Bitmap(path)
                except Exception as e:
                    print("Failed to load image")
                    image = create_white_image(250, 190)  # Fallback to a white image

                imageView.Image = image

                ############################################################
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

                ############################################################
                # Create a horizontal StackLayout for used material information
                usedMaterialInfoLayout = forms.StackLayout()
                usedMaterialInfoLayout.Spacing = 3
                
                usedMaterialInfo = usedData ######### Need to change
                
                desired_font_size = 10
                
                for info in usedMaterialInfo:
                    # Create and add labels with the desired font size to the layout.
                    usedMaterialInfoLayout.Items.Add(create_label_with_font(info, desired_font_size))
                
                # Encapsulate descriptionsLayout in a Scrollable for horizontal scrolling
                usedMaterialInfoScrollable = forms.Scrollable()
                usedMaterialInfoScrollable.Content = usedMaterialInfoLayout
                
                # Set the size of the Scrollable to match the imageView's size
                # Here, the height is arbitrary since it's a horizontal scroll
                usedMaterialInfoScrollable.Width = imageView.Width

                ############################################################
                link_button = forms.LinkButton(Text="Open Website")
                link_button.Click += lambda sender, e, url=urrl: webbrowser.open(url)
                
                
                # Checkbox and Label Pair
                checkBoxLabelLayout = forms.StackLayout()  # Horizontal layout for checkbox and label
                checkBoxLabelLayout.Orientation = forms.Orientation.Horizontal
                checkBoxLabelLayout.Spacing = 5
                
                checkBox = forms.CheckBox() 
                checkBox.CheckedChanged += self.on_checked_changed
                self.checkBoxes.append(checkBox)
                
                checkBoxLabel = forms.Label(Text="Show in Rhino")  # Custom font label
                checkBoxLabel.Font = drawing.Font("Arial Bold", 13)  # Set the font here
                
                checkBoxLabelLayout.Items.Add(checkBox)
                checkBoxLabelLayout.Items.Add(checkBoxLabel)
                
                
                # Add the imageView, descriptionScrollable, and checkBox to the unitLayout
                unitLayout.Items.Add(imageView)
                unitLayout.Items.Add(usedMaterialInfoScrollable)
                unitLayout.Items.Add(descriptionScrollable)  # Add the scrollable descriptions
                unitLayout.Items.Add(link_button)
                # unitLayout.Items.Add(checkBoxLabelLayout)
    
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


class openingWindow(forms.Form):  # Use Dialog[bool] for a modal dialog
    def __init__(self):
        super(openingWindow, self).__init__()
        self.Title = "Image Viewer"
        
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
        self.usedDataList = usedDataList
        self.populate_images()

    def populate_images(self):
        images_per_row = rowNum
        row = []
        count = 0
        
        for path, data, urrl, usedData in zip(self.imagePaths, self.dataList, self.urlList, self.usedDataList):

            try:
                unitLayout = forms.StackLayout()
                unitLayout.Orientation = forms.Orientation.Vertical
                unitLayout.Spacing = 5
                unitLayout.Padding = drawing.Padding(10)
    
                imageView = forms.ImageView()
                imageView.Size = drawing.Size(250, 250)  # Fixed size for the image
                
                try:
                    image = drawing.Bitmap(path)
                except Exception as e:
                    print("Failed to load image")
                    image = create_white_image(250, 190)  # Fallback to a white image

                imageView.Image = image

                ############################################################
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

                ############################################################
                # Create a horizontal StackLayout for used material information
                usedMaterialInfoLayout = forms.StackLayout()
                usedMaterialInfoLayout.Spacing = 3
                
                usedMaterialInfo = usedData ######### Need to change
                
                desired_font_size = 10

                print()
                
                if not isinstance(usedMaterialInfo, list):
                    # for info in usedMaterialInfo:
                    # Create and add labels with the desired font size to the layout.
                    usedMaterialInfoLayout.Items.Add(create_label_with_font(usedMaterialInfo, desired_font_size))
                else:
                    for info in usedMaterialInfo:
                        usedMaterialInfoLayout.Items.Add(create_label_with_font(info, desired_font_size))
                
                # Encapsulate descriptionsLayout in a Scrollable for horizontal scrolling
                usedMaterialInfoScrollable = forms.Scrollable()
                usedMaterialInfoScrollable.Content = usedMaterialInfoLayout
                
                # Set the size of the Scrollable to match the imageView's size
                # Here, the height is arbitrary since it's a horizontal scroll
                usedMaterialInfoScrollable.Width = imageView.Width

                ############################################################
                link_button = forms.LinkButton(Text="Open Website")
                link_button.Click += lambda sender, e, url=urrl: webbrowser.open(url)
                
                
                # Checkbox and Label Pair
                checkBoxLabelLayout = forms.StackLayout()  # Horizontal layout for checkbox and label
                checkBoxLabelLayout.Orientation = forms.Orientation.Horizontal
                checkBoxLabelLayout.Spacing = 5
                
                checkBox = forms.CheckBox() 
                checkBox.CheckedChanged += self.on_checked_changed
                self.checkBoxes.append(checkBox)
                
                checkBoxLabel = forms.Label(Text="Show in Rhino")  # Custom font label
                checkBoxLabel.Font = drawing.Font("Arial Bold", 13)  # Set the font here
                
                checkBoxLabelLayout.Items.Add(checkBox)
                checkBoxLabelLayout.Items.Add(checkBoxLabel)
                
                
                # Add the imageView, descriptionScrollable, and checkBox to the unitLayout
                unitLayout.Items.Add(imageView)
                unitLayout.Items.Add(usedMaterialInfoScrollable)
                unitLayout.Items.Add(descriptionScrollable)  # Add the scrollable descriptions
                unitLayout.Items.Add(link_button)
                # unitLayout.Items.Add(checkBoxLabelLayout)
    
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


showNum = 100

if showType == "innerMaterial":
    totalInfo = showData.usedMatDict['innerMaterial']
    # print(len(showData.usedMatDict['window']))

    # layer / module_ID / ['info']
    # print(totalInfo[0][0]['info'].foto1)
    # print(totalInfo[0])
    # print(totalInfo[0][0])
    # print(len(totalInfo))

    # Make list of used material for "Board"
    layer_imgPath = []
    layer_url = []
    layer_description = []
    layer_useInfo = []
    topic = []

    for layerKey in totalInfo:
        layer_imgPath.append(totalInfo[layerKey][0]['info'].foto1)
        layer_url.append(totalInfo[layerKey][0]['info'].url)
        li = ["{}: {}".format(attr, getattr(totalInfo[layerKey][0]['info'], attr, None)) for attr in chosenItem]
        layer_description.append(li)


        # For board
        compPie = 0
        cutPie = 0
        usePie = 0
        # For substructure / substructureInfill
        usedLength = 0
        # For substructureInfill / paint
        usedArea = 0

        for moduleKey in totalInfo[layerKey]:
            if totalInfo[layerKey][moduleKey]['materialType'] == 'board':
                moduleInfo = totalInfo[layerKey][moduleKey]
                compPie += moduleInfo['completedPiece']
                cutPie += moduleInfo['cuttedPiece']
                usePie += moduleInfo['usedPiece']
            
            elif totalInfo[layerKey][moduleKey]['materialType'] == 'substructInfill':
                moduleInfo = totalInfo[layerKey][moduleKey]
                usedLength += moduleInfo['usedLength']
                usedArea += moduleInfo['usedArea']
            
            elif totalInfo[layerKey][moduleKey]['materialType'] == 'substruct':
                moduleInfo = totalInfo[layerKey][moduleKey]
                usedLength += moduleInfo['usedLength']
            
            elif totalInfo[layerKey][moduleKey]['materialType'] == 'paint':
                moduleInfo = totalInfo[layerKey][moduleKey]
                usedArea += moduleInfo['usedArea']


        if totalInfo[layerKey][0]['materialType'] == 'board':
            temp = []
            temp.append("layer: {}".format(layerKey))
            temp.append("type: board")
            temp.append("usedPiece: {}".format(usePie))
            temp.append("completePiece: {}".format(compPie))
            temp.append("cuttedPiece: {}".format(cutPie))
            layer_useInfo.append(temp)
        
        elif totalInfo[layerKey][0]['materialType'] == 'substructInfill':
            temp = []
            temp.append("layer: {}".format(layerKey))
            temp.append("type: substructureInfill")
            temp.append("usedLength: {} cm".format(usedLength))
            temp.append("usedArea: {} cm2".format(usedArea))
            layer_useInfo.append(temp)
        
        elif totalInfo[layerKey][0]['materialType'] == 'substruct':
            temp = []
            temp.append("layer: {}".format(layerKey))
            temp.append("type: substructure")
            temp.append("usedLength: {} cm".format(usedLength))
            layer_useInfo.append(temp)
        
        elif totalInfo[layerKey][0]['materialType'] == 'paint':
            temp = []
            temp.append("layer: {}".format(layerKey))
            temp.append("type: paint")
            temp.append("usedArea: {} cm2".format(usedArea))
            layer_useInfo.append(temp)

    imagePaths = layer_imgPath
    urlList = layer_url
    dataList = layer_description
    usedDataList = layer_useInfo


    def show_check_box_form():
        form = innerMaterialWindow()
        form.Show()

    # A simple function to simulate a value listener that polls for checkbox state changes
    def poll_checkbox_states():
        # Default to all False if not set
        return sc.sticky.get('checkbox_states', [False] * showNum)


if showType == "opening":
    windowInfo = showData.usedMatDict['window']
    doorInfo = showData.usedMatDict['door']

    # Make list of used material for "Board"
    layer_imgPath = []
    layer_url = []
    layer_description = []
    layer_useInfo = []
    topic = []
    for wData in windowInfo:
        layer_imgPath.append(wData['foto1'])
        layer_url.append(wData['url'])
        li = ["{}: {}".format(attr, wData[attr]) for attr in chosenItem]
        layer_description.append(li)
        layer_useInfo.append("type : Window")
    
    for dData in doorInfo:
        layer_imgPath.append(dData['foto1'])
        layer_url.append(dData['url'])
        li = ["{}: {}".format(attr, dData[attr]) for attr in chosenItem]
        layer_description.append(li)
        layer_useInfo.append("type : Door")

    imagePaths = layer_imgPath
    urlList = layer_url
    dataList = layer_description
    usedDataList = layer_useInfo


    def show_check_box_form():
        form = openingWindow()
        form.Show()

    # A simple function to simulate a value listener that polls for checkbox state changes
    def poll_checkbox_states():
        # Default to all False if not set
        return sc.sticky.get('checkbox_states', [False] * showNum)


if showType == "outerMaterial":
    layer_imgPath = []
    layer_url = []
    layer_description = []
    layer_useInfo = []
    topic = []
    # print(showData.usedMatDict['outerMaterial'])
    if showData.usedMatDict['outerMaterial']['type'] == 'tile':
        tileInfo = showData.usedMatDict['outerMaterial']['matInfo']
        print(tileInfo[0])

        for layerKey in tileInfo:
            layer_imgPath.append(tileInfo[layerKey]['info']['foto1'])
            layer_url.append(tileInfo[layerKey]['info']['url'])
            li = ["{}: {}".format(attr, tileInfo[layerKey]['info'][attr]) for attr in chosenItem]
            layer_description.append(li)
        
            temp = []
            temp.append("tile_{}".format(layerKey))
            # temp.append("type: tile")
            temp.append("usedQuantity: {}".format(tileInfo[layerKey]['usedQuantity']))
            layer_useInfo.append(temp)
    
    elif showData.usedMatDict['outerMaterial']['type'] == 'normal':
        totalInfo = showData.usedMatDict['outerMaterial']['matInfo']

        for layerKey in totalInfo:
            layer_imgPath.append(totalInfo[layerKey][0]['info'].foto1)
            layer_url.append(totalInfo[layerKey][0]['info'].url)
            li = ["{}: {}".format(attr, getattr(totalInfo[layerKey][0]['info'], attr, None)) for attr in chosenItem]
            layer_description.append(li)


            # For board
            compPie = 0
            cutPie = 0
            usePie = 0
            # For substructure / substructureInfill
            usedLength = 0
            # For substructureInfill / paint
            usedArea = 0

            for moduleKey in totalInfo[layerKey]:
                if totalInfo[layerKey][moduleKey]['materialType'] == 'board':
                    moduleInfo = totalInfo[layerKey][moduleKey]
                    compPie += moduleInfo['completedPiece']
                    cutPie += moduleInfo['cuttedPiece']
                    usePie += moduleInfo['usedPiece']
                
                elif totalInfo[layerKey][moduleKey]['materialType'] == 'substructInfill':
                    moduleInfo = totalInfo[layerKey][moduleKey]
                    usedLength += moduleInfo['usedLength']
                    usedArea += moduleInfo['usedArea']
                
                elif totalInfo[layerKey][moduleKey]['materialType'] == 'substruct':
                    moduleInfo = totalInfo[layerKey][moduleKey]
                    usedLength += moduleInfo['usedLength']
                
                elif totalInfo[layerKey][moduleKey]['materialType'] == 'paint':
                    moduleInfo = totalInfo[layerKey][moduleKey]
                    usedArea += moduleInfo['usedArea']


            if totalInfo[layerKey][0]['materialType'] == 'board':
                temp = []
                temp.append("layer: {}".format(layerKey))
                temp.append("type: board")
                temp.append("usedPiece: {}".format(usePie))
                temp.append("completePiece: {}".format(compPie))
                temp.append("cuttedPiece: {}".format(cutPie))
                layer_useInfo.append(temp)
            
            elif totalInfo[layerKey][0]['materialType'] == 'substructInfill':
                temp = []
                temp.append("layer: {}".format(layerKey))
                temp.append("type: substructureInfill")
                temp.append("usedLength: {} cm".format(usedLength))
                temp.append("usedArea: {} cm2".format(usedArea))
                layer_useInfo.append(temp)
            
            elif totalInfo[layerKey][0]['materialType'] == 'substruct':
                temp = []
                temp.append("layer: {}".format(layerKey))
                temp.append("type: substructure")
                temp.append("usedLength: {} cm".format(usedLength))
                layer_useInfo.append(temp)
            
            elif totalInfo[layerKey][0]['materialType'] == 'paint':
                temp = []
                temp.append("layer: {}".format(layerKey))
                temp.append("type: paint")
                temp.append("usedArea: {} cm2".format(usedArea))
                layer_useInfo.append(temp)


    imagePaths = layer_imgPath
    urlList = layer_url
    dataList = layer_description
    usedDataList = layer_useInfo

    def show_check_box_form():
        form = innerMaterialWindow()
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

