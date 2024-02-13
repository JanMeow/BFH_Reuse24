// const data = require("./window_imputation.json");
// console.log(data.length); // Outputs: John Doe

const fs = require("fs");
const path = require("path");

// Read JSON data from a file
const jsonData = JSON.parse(
  fs.readFileSync(
    "C:/Users/User/Documents/GitHub/BFH_Reuse24/Kevin/DB/window_imputation.json",
    "utf8"
  )
);

console.log(jsonData.length);

// Specify the folder path
const folderPath =
  "C:/Users/User/Documents/GitHub/BFH_Reuse24/Kevin/DB/BFH_DB/Pictures_gruner/1_221114_Foto_Bau09/Foto_Bau09";

// Read the directory contents
fs.readdir(folderPath, (err, files) => {
  if (err) {
    console.error("Error reading the directory", err);
    return;
  }

  // Filter for image files (assuming jpg, png, gif)
  const imageFiles = files.filter((file) =>
    /\.(jpg|jpeg|png|gif)$/i.test(file)
  );

  // Create full paths
  const newImages = imageFiles.map((file) => path.join(folderPath, file));

  // Replace the "image" field in each item
  jsonData.forEach((item, index) => {
    if (newImages[index]) {
      item.image = newImages[index];
    }
  });

  // Write the updated JSON data back to a file
  fs.writeFileSync(
    "C:/Users/User/Documents/GitHub/BFH_Reuse24/Kevin/DB/demo_window_imputation.json",
    JSON.stringify(jsonData, null, 2),
    "utf8"
  );
});
