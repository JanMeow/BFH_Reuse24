import Rhino
import Rhino.Geometry as rg
import Eto.Forms as forms
import Eto.Drawing as drawing
import webbrowser
import scriptcontext as sc

# Imports from
from Rhino.UI import *
from Eto.Forms import *
from Eto.Drawing import *

# Imports
import Rhino.UI
import Eto
import System

from Rhino import RhinoDoc, Display
from System.Drawing import Bitmap, Graphics, Rectangle, Size
from System.Drawing.Imaging import ImageFormat
import System.IO



if winHeight is None:
    winHeight = 800
if rowNum is None:
    rowNum = 4

def create_label_with_font(text, font_size, font_family="Arial"):
    label = forms.Label(Text=text)
    label.Font = drawing.Font(font_family, font_size)
    return label

## Original One
def create_white_image(width, height):
    """Create a white bitmap image of specified width and height."""
    white_image = drawing.Bitmap(width, height, drawing.PixelFormat.Format32bppRgb)
    text = "     _(:3 」∠ )_\n Image not found"
    with drawing.Graphics(white_image) as g:
        g.Clear(drawing.Colors.Gray)  # Fill the image with white color
        font = drawing.Font("Arial", 12)  # You can adjust the font and size
        text_brush = drawing.SolidBrush(drawing.Colors.White)
        text_size = g.MeasureString(font, text)
        text_location = drawing.PointF((width - text_size.Width) / 2, (height - text_size.Height) / 2)
        g.DrawText(font, text_brush, text_location, text)



    return white_image

"""countNum = 0
showGeo = []
def create_white_image2(width, height):
    global countNum
    countNum += 1
    geo = missGeo[countNum%len(missGeo)]
    bbox = geo.GetBoundingBox(True)
    
    # Get the active Rhino document
    doc = RhinoDoc.ActiveDoc
    view = doc.Views.ActiveView
    viewport = view.ActiveViewport

    oriCamSet = {}
    oriCamSet['CameraTarget'] = viewport.CameraTarget
    oriCamSet['CameraLocation'] = viewport.CameraLocation
    
    # Set the camera parameters
    # camera_location = Rhino.Geometry.Point3d(1000, 1000, 1000)
    # target_point = Rhino.Geometry.Point3d(0, 0, 0)
    # viewport.Camera35mmLensLength = 50
    # viewport.SetCameraLocations(target_point, camera_location)
    
    # Redraw the view to update the viewport
    viewport.ZoomBoundingBox(bbox)
    view.Redraw()

    # Capture the current view to a bitmap
    captured_bitmap = view.CaptureToBitmap()

    # Resize the captured image to the desired dimensions using System.Drawing
    resized_image = Bitmap(width, height)
    with Graphics.FromImage(resized_image) as g:
        rect = Rectangle(0, 0, width, height)
        g.DrawImage(captured_bitmap, rect)

    # Convert System.Drawing.Bitmap to Eto.Drawing.Bitmap
    eto_stream = System.IO.MemoryStream()
    resized_image.Save(eto_stream, ImageFormat.Png)
    eto_stream.Position = 0  # Reset stream position after saving
    eto_bitmap = drawing.Bitmap(eto_stream)

    # Cleanup
    eto_stream.Dispose()
    captured_bitmap.Dispose()
    resized_image.Dispose()


    viewport.SetCameraLocations(oriCamSet['CameraTarget'], oriCamSet['CameraLocation'])
    # Redraw the view to update the viewport
    view.Redraw()

    return eto_bitmap
"""

imgWidth = 250

class innerMaterialWindow(forms.Form):  # Use Dialog[bool] for a modal dialog
    def __init__(self):
        super(innerMaterialWindow, self).__init__()
        self.Title = "Image Viewer"

        self.layout = forms.DynamicLayout()
        self.layout.Height = winHeight

        self.scrollable = forms.Scrollable()
        self.imageLayout = forms.DynamicLayout()
        self.imageLayout.Padding = drawing.Padding(10, 10, 20, 30)
        self.scrollable.Content = self.imageLayout
        self.layout.AddRow(self.scrollable)
        self.Content = self.layout

        self.populate_images(imagePaths, dataList, urlList, usedDataList)

    def populate_images(self, imagePaths, dataList, urlList, usedDataList):
        images_per_row = rowNum
        row = []
        count = 0
        
        for path, data, urrl, usedData in zip(imagePaths, dataList, urlList, usedDataList):

            try:
                unitLayout = forms.StackLayout()
                unitLayout.Orientation = forms.Orientation.Vertical
                unitLayout.Spacing = 1
                unitLayout.Padding = drawing.Padding(10, 0, 10, 15)
    
                imageView = forms.ImageView()
                imageView.Size = drawing.Size(imgWidth, 200)  # Fixed size for the image
                
                try:
                    image = drawing.Bitmap(path)
                except Exception as e:
                    print("Failed to load image")
                    image = create_white_image(imgWidth, 192)  # Fallback to a white image

                imageView.Image = image

                ############################################################
                # Create a horizontal StackLayout for descriptions
                descriptionsLayout = forms.StackLayout()
                descriptionsLayout.Spacing = 1
                
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
                
                
                # Add the imageView, descriptionScrollable, and checkBox to the unitLayout
                unitLayout.Items.Add(imageView)
                unitLayout.Items.Add(usedMaterialInfoScrollable)
                if showDes:
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
    
    def update(self, imagePaths, dataList, urlList, usedDataList):
    # Clear existing content from the image layout and repopulate it
        self.imageLayout.Clear()  # Clear existing items from the layout
        self.populate_images(imagePaths, dataList, urlList, usedDataList)
        self.scrollable.Content = None  # Detach the old layout
        self.scrollable.Content = self.imageLayout  # Attach the updated layout



showNum = 100
totalCal = False if len(showData)==1 else True

if showType == "innerMaterial":
    
    # print(len(showData.usedMatDict['window']))

    """
    # layer / module_ID / ['info']
    # print(totalInfo[0][0]['info'].foto1)
    # print(totalInfo[0])
    # print(totalInfo[0][0])
    # print(len(totalInfo))
    """

    infoDict = {}
    for showDataOne in showData:
        totalInfo = showDataOne.usedMatDict['innerMaterial']
        for layerKey in totalInfo:
            uuidKey = totalInfo[layerKey][0]['info'].uuid
            if uuidKey not in infoDict.keys():
                infoDict[uuidKey] = {}
                infoDict[uuidKey]['layer_imgPath'] = totalInfo[layerKey][0]['info'].foto1
                infoDict[uuidKey]['layer_url'] = totalInfo[layerKey][0]['info'].url
                li = ["{}: {}".format(attr, getattr(totalInfo[layerKey][0]['info'], attr, None)) for attr in chosenItem]
                infoDict[uuidKey]['layer_description'] = li
                infoDict[uuidKey]['layer_useInfo'] = None

                # For board
                infoDict[uuidKey]["compPie"] = 0
                infoDict[uuidKey]["cutPie"] = 0
                infoDict[uuidKey]["usePie"] = 0
                # For substructure / substructureInfill
                infoDict[uuidKey]["usedLength"] = 0
                # For substructureInfill / paint
                infoDict[uuidKey]["usedArea"] = 0
            

            for moduleKey in totalInfo[layerKey]:
                if totalInfo[layerKey][moduleKey]['materialType'] == 'board':
                    moduleInfo = totalInfo[layerKey][moduleKey]
                    infoDict[uuidKey]["compPie"] += moduleInfo['completedPiece']
                    infoDict[uuidKey]["cutPie"] += moduleInfo['cuttedPiece']
                    infoDict[uuidKey]["usePie"] += moduleInfo['usedPiece']
                
                elif totalInfo[layerKey][moduleKey]['materialType'] == 'substructInfill':
                    moduleInfo = totalInfo[layerKey][moduleKey]
                    infoDict[uuidKey]["usedLength"] += moduleInfo['usedLength']
                    infoDict[uuidKey]["usedArea"] += moduleInfo['usedArea']
                
                elif totalInfo[layerKey][moduleKey]['materialType'] == 'substruct':
                    moduleInfo = totalInfo[layerKey][moduleKey]
                    infoDict[uuidKey]["usedLength"] += moduleInfo['usedLength']
                
                elif totalInfo[layerKey][moduleKey]['materialType'] == 'paint':
                    moduleInfo = totalInfo[layerKey][moduleKey]
                    infoDict[uuidKey]["usedArea"] += moduleInfo['usedArea']
                
            
            if totalInfo[layerKey][0]['materialType'] == 'board':
                temp = []
                if not totalCal:
                    infoDict[uuidKey]['layerNum'] = layerKey
                    temp.append("layer: {}".format(layerKey))
                temp.append("type: board")
                temp.append("usedPiece: {}".format(infoDict[uuidKey]["usePie"]))
                temp.append("completePiece: {}".format(infoDict[uuidKey]["compPie"]))
                temp.append("cuttedPiece: {}".format(infoDict[uuidKey]["cutPie"]))
                infoDict[uuidKey]['layer_useInfo'] = temp
            
            elif totalInfo[layerKey][0]['materialType'] == 'substructInfill':
                temp = []
                if not totalCal:
                    infoDict[uuidKey]['layerNum'] = layerKey
                    temp.append("layer: {}".format(layerKey))
                temp.append("type: substructureInfill")
                temp.append("usedLength: {} cm".format(infoDict[uuidKey]["usedLength"]))
                temp.append("usedArea: {} cm2".format(infoDict[uuidKey]["usedArea"]))
                infoDict[uuidKey]['layer_useInfo'] = temp
            
            elif totalInfo[layerKey][0]['materialType'] == 'substruct':
                temp = []
                if not totalCal:
                    infoDict[uuidKey]['layerNum'] = layerKey
                    temp.append("layer: {}".format(layerKey))
                temp.append("type: substructure")
                temp.append("usedLength: {} cm".format(infoDict[uuidKey]["usedLength"]))
                infoDict[uuidKey]['layer_useInfo'] = temp
            
            elif totalInfo[layerKey][0]['materialType'] == 'paint':
                temp = []
                if not totalCal:
                    infoDict[uuidKey]['layerNum'] = layerKey
                    temp.append("layer: {}".format(layerKey))
                temp.append("type: paint")
                temp.append("usedArea: {} cm2".format(infoDict[uuidKey]["usedArea"]))
                infoDict[uuidKey]['layer_useInfo'] = temp

    layer_imgPath = []
    layer_url = []
    layer_description = []
    layer_useInfo = []
    for uuidKey in infoDict:
        layer_imgPath.append(infoDict[uuidKey]['layer_imgPath'])
        layer_url.append(infoDict[uuidKey]['layer_url'])
        layer_description.append(infoDict[uuidKey]['layer_description'])
        layer_useInfo.append(infoDict[uuidKey]['layer_useInfo'])
    
    if not totalCal:
        layer_order = [infoDict[uuidKey]['layerNum'] for uuidKey in infoDict]

        # Zip all lists together with the order list
        zipped_layers = zip(layer_order, layer_imgPath, layer_url, layer_description, layer_useInfo)

        # Sort by the order specified in layer_order
        sorted_layers = sorted(zipped_layers)

        # Unzip the lists
        unzipped_layers = list(zip(*sorted_layers))

        # Extracting lists from the sorted zipped list
        sorted_layer_order = list(unzipped_layers[0])
        layer_imgPath = list(unzipped_layers[1])
        layer_url = list(unzipped_layers[2])
        layer_description = list(unzipped_layers[3])
        layer_useInfo = list(unzipped_layers[4])


if showType == "opening":
    infoDict = {}
    for showDataOne in showData:
        windowInfo = showDataOne.usedMatDict['window']
        doorInfo = showDataOne.usedMatDict['door']

        for wData in windowInfo:
            window_uuid = wData['uuid']
            if window_uuid not in infoDict.keys():
                infoDict[window_uuid] = {}
                infoDict[window_uuid]['layer_imgPath'] = wData['foto1']
                infoDict[window_uuid]['layer_url'] = wData['url']
                li = ["{}: {}".format(attr, wData[attr]) for attr in chosenItem]
                infoDict[window_uuid]['layer_description'] = li
                infoDict[window_uuid]["useQuantity"] = 0
                infoDict[window_uuid]["openType"] = "window"
                
            infoDict[window_uuid]["useQuantity"] += 1
            
            temp = []
            temp.append("type : Window")
            temp.append("usedPiece: {}".format(infoDict[window_uuid]["useQuantity"]))
            infoDict[window_uuid]["layer_useInfo"] = temp

        for dData in doorInfo:
            door_uuid = dData['uuid']
            if door_uuid not in infoDict.keys():
                infoDict[door_uuid] = {}
                infoDict[door_uuid]['layer_imgPath'] = dData['foto1']
                infoDict[door_uuid]['layer_url'] = dData['url']
                li = ["{}: {}".format(attr, dData[attr]) for attr in chosenItem]
                infoDict[door_uuid]['layer_description'] = li
                infoDict[door_uuid]["useQuantity"] = 0
                infoDict[door_uuid]["openType"] = "door"
                
            infoDict[door_uuid]["useQuantity"] += 1
            
            temp = []
            temp.append("type : Door")
            temp.append("usedPiece: {}".format(infoDict[door_uuid]["useQuantity"]))
            infoDict[door_uuid]["layer_useInfo"] = temp
            

    layer_imgPath = []
    layer_url = []
    layer_description = []
    layer_useInfo = []
    for uuidKey in infoDict:
        layer_imgPath.append(infoDict[uuidKey]['layer_imgPath'])
        layer_url.append(infoDict[uuidKey]['layer_url'])
        layer_description.append(infoDict[uuidKey]['layer_description'])
        layer_useInfo.append(infoDict[uuidKey]['layer_useInfo'])


if showType == "outerMaterial":
    infoDict = {}
    tileNum = 0
    matID = 0
    for showDataOne in showData:
        if showDataOne.usedMatDict['outerMaterial']['type'] == 'tile':
            tileInfo = showDataOne.usedMatDict['outerMaterial']['matInfo']
            for layerKey in tileInfo:
                uuidKey = tileInfo[layerKey]['info']['uuid']
                
                if uuidKey not in infoDict.keys():
                    tileNum += 1
                    matID += 1
                    infoDict[uuidKey] = {}
                    infoDict[uuidKey]['layer_imgPath'] = tileInfo[layerKey]['info']['foto1']
                    infoDict[uuidKey]['layer_url'] = tileInfo[layerKey]['info']['url']
                    li = ["{}: {}".format(attr, tileInfo[layerKey]['info'][attr]) for attr in chosenItem]
                    infoDict[uuidKey]['layer_description'] = li
                    infoDict[uuidKey]['layer_useInfo'] = None
                    infoDict[uuidKey]['usedQuantity'] = 0
                    infoDict[uuidKey]['tileNum'] = tileNum

                    infoDict[uuidKey]['facadeType'] = 'tile'
                    infoDict[uuidKey]['matID'] = matID


                infoDict[uuidKey]['usedQuantity'] += tileInfo[layerKey]['usedQuantity']

                temp = []
                temp.append("tile_{}".format(infoDict[uuidKey]['tileNum']))
                temp.append("usedQuantity: {}".format(infoDict[uuidKey]['usedQuantity']))
                infoDict[uuidKey]['layer_useInfo'] = temp


        elif showDataOne.usedMatDict['outerMaterial']['type'] == 'normal':
            totalInfo = showDataOne.usedMatDict['outerMaterial']['matInfo']

            for layerKey in totalInfo:
                uuidKey = totalInfo[layerKey][0]['info'].uuid
                if uuidKey not in infoDict.keys():
                    matID += 1
                    infoDict[uuidKey] = {}
                    infoDict[uuidKey]['layer_imgPath'] = totalInfo[layerKey][0]['info'].foto1
                    infoDict[uuidKey]['layer_url'] = totalInfo[layerKey][0]['info'].url
                    li = ["{}: {}".format(attr, getattr(totalInfo[layerKey][0]['info'], attr, None)) for attr in chosenItem]
                    infoDict[uuidKey]['layer_description'] = li
                    infoDict[uuidKey]['layer_useInfo'] = None

                    infoDict[uuidKey]['facadeType'] = 'normal'
                    infoDict[uuidKey]['matID'] = matID

                    # For board
                    infoDict[uuidKey]["compPie"] = 0
                    infoDict[uuidKey]["cutPie"] = 0
                    infoDict[uuidKey]["usePie"] = 0
                    # For substructure / substructureInfill
                    infoDict[uuidKey]["usedLength"] = 0
                    # For substructureInfill / paint
                    infoDict[uuidKey]["usedArea"] = 0
                

                for moduleKey in totalInfo[layerKey]:
                    if totalInfo[layerKey][moduleKey]['materialType'] == 'board':
                        moduleInfo = totalInfo[layerKey][moduleKey]
                        infoDict[uuidKey]["compPie"] += moduleInfo['completedPiece']
                        infoDict[uuidKey]["cutPie"] += moduleInfo['cuttedPiece']
                        infoDict[uuidKey]["usePie"] += moduleInfo['usedPiece']
                    
                    elif totalInfo[layerKey][moduleKey]['materialType'] == 'substructInfill':
                        moduleInfo = totalInfo[layerKey][moduleKey]
                        infoDict[uuidKey]["usedLength"] += moduleInfo['usedLength']
                        infoDict[uuidKey]["usedArea"] += moduleInfo['usedArea']
                    
                    elif totalInfo[layerKey][moduleKey]['materialType'] == 'substruct':
                        moduleInfo = totalInfo[layerKey][moduleKey]
                        infoDict[uuidKey]["usedLength"] += moduleInfo['usedLength']
                    
                    elif totalInfo[layerKey][moduleKey]['materialType'] == 'paint':
                        moduleInfo = totalInfo[layerKey][moduleKey]
                        infoDict[uuidKey]["usedArea"] += moduleInfo['usedArea']
                    
                
                if totalInfo[layerKey][0]['materialType'] == 'board':
                    temp = []
                    if not totalCal:
                        infoDict[uuidKey]['layerNum'] = layerKey
                        temp.append("layer: {}".format(layerKey))
                    temp.append("type: board")
                    temp.append("usedPiece: {}".format(infoDict[uuidKey]["usePie"]))
                    temp.append("completePiece: {}".format(infoDict[uuidKey]["compPie"]))
                    temp.append("cuttedPiece: {}".format(infoDict[uuidKey]["cutPie"]))
                    infoDict[uuidKey]['layer_useInfo'] = temp
                
                elif totalInfo[layerKey][0]['materialType'] == 'substructInfill':
                    temp = []
                    if not totalCal:
                        infoDict[uuidKey]['layerNum'] = layerKey
                        temp.append("layer: {}".format(layerKey))
                    temp.append("type: substructureInfill")
                    temp.append("usedLength: {} cm".format(infoDict[uuidKey]["usedLength"]))
                    temp.append("usedArea: {} cm2".format(infoDict[uuidKey]["usedArea"]))
                    infoDict[uuidKey]['layer_useInfo'] = temp
                
                elif totalInfo[layerKey][0]['materialType'] == 'substruct':
                    temp = []
                    if not totalCal:
                        infoDict[uuidKey]['layerNum'] = layerKey
                        temp.append("layer: {}".format(layerKey))
                    temp.append("type: substructure")
                    temp.append("usedLength: {} cm".format(infoDict[uuidKey]["usedLength"]))
                    infoDict[uuidKey]['layer_useInfo'] = temp
                
                elif totalInfo[layerKey][0]['materialType'] == 'paint':
                    temp = []
                    if not totalCal:
                        infoDict[uuidKey]['layerNum'] = layerKey
                        temp.append("layer: {}".format(layerKey))
                    temp.append("type: paint")
                    temp.append("usedArea: {} cm2".format(infoDict[uuidKey]["usedArea"]))
                    infoDict[uuidKey]['layer_useInfo'] = temp


    layer_imgPath = []
    layer_url = []
    layer_description = []
    layer_useInfo = []
    for uuidKey in infoDict:
        layer_imgPath.append(infoDict[uuidKey]['layer_imgPath'])
        layer_url.append(infoDict[uuidKey]['layer_url'])
        layer_description.append(infoDict[uuidKey]['layer_description'])
        layer_useInfo.append(infoDict[uuidKey]['layer_useInfo'])


    if not totalCal:
        if infoDict[uuidKey]['facadeType'] == 'tile':
            layer_order = [infoDict[uuidKey]['tileNum'] for uuidKey in infoDict]
        elif infoDict[uuidKey]['facadeType'] == 'normal':
            layer_order = [infoDict[uuidKey]['layerNum'] for uuidKey in infoDict]

    else:
        layer_order = [infoDict[uuidKey]['matID'] for uuidKey in infoDict]
    
            # Zip all lists together with the order list
    zipped_layers = zip(layer_order, layer_imgPath, layer_url, layer_description, layer_useInfo)

    # Sort by the order specified in layer_order
    sorted_layers = sorted(zipped_layers)

    # Unzip the lists
    unzipped_layers = list(zip(*sorted_layers))

    # Extracting lists from the sorted zipped list
    sorted_layer_order = list(unzipped_layers[0])
    layer_imgPath = list(unzipped_layers[1])
    layer_url = list(unzipped_layers[2])
    layer_description = list(unzipped_layers[3])
    layer_useInfo = list(unzipped_layers[4])


imagePaths = layer_imgPath
urlList = layer_url
dataList = layer_description
usedDataList = layer_useInfo


def RunScript():
    # Ensure the form exists and is visible
    if "my_form" in globals():
        if my_form.Visible:
            # Update the form with the current number input
            my_form.update(imagePaths, dataList, urlList, usedDataList)
        else:
            print("not visible")
            # The form was closed, remove it
            del globals()["my_form"]
    else:
        # Form does not exist, create and show it
        global my_form
        my_form =  innerMaterialWindow()
        my_form.Show()

    return 0


if open:
    RunScript()
else:
    if "my_form" in globals():
        my_form.Close()
        del globals()["my_form"]

