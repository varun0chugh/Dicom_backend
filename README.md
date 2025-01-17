DICOM Viewer and Image Processing Application
Overview
This application consists of a React Frontend and a Flask Backend designed to upload, process, and visualize DICOM (medical imaging) files. The application allows image adjustments like brightness, contrast, cropping, zooming, panning, and window-level adjustments.
How It Works
Upload DICOM File:

The frontend sends the DICOM file to the /upload endpoint.
Metadata and a normalized image are extracted and stored.
View Image and Metadata:

Metadata is fetched from /metadata.
The image is fetched from /image.
Image Adjustments:
you can right click on the image for adjustments.

Adjustments (e.g., brightness, contrast, cropping) are made via respective endpoints (/adjust, /crop, /zoom, etc.).
Processed Output:

All processed images are saved in the output directory.
i will provide a .dcm file for testing.


Setup Instructions
1. Clone the Repository

git clone https://github.com/<your-username>/dicom_frontend.git
git clone https://github.com/<your-username>/dicom_backend.git
cd medical-image-annotation-saas
2. Navigate to the Frontend Directory

cd frontend
3. Install Dependencies
Install the required dependencies using npm or yarn:


npm install
4. Run the Development Server
Start the frontend server in development mode:

npm start
The application will be accessible at http://localhost:3000.

5. Build for Production
To create an optimized production build:


npm run build
6. Run Using Docker
Ensure Docker is Installed: Make sure Docker is installed and running on your machine.

Build and Run Docker Containers:

From the root project directory:

docker-compose up --build
Access the Application:

Frontend: http://localhost:3000
Backend: http://localhost:5000 (if backend is implemented and included in docker-compose.yml)
