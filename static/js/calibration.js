const video = document.getElementById("videoPlayer");

document.getElementById("videoUpload").addEventListener("change", function(e) {
    const file = e.target.files[0];
    const url = URL.createObjectURL(file);
    video.src = url;
});

function captureFrame() {

    video.pause();

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const frameData = canvas.toDataURL("image/jpeg");

    fetch("/upload-frame", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ frame: frameData })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "ready") {
            alert("Draw ROI in OpenCV window");
        } else {
            alert("Error processing frame");
        }
    });
}

function saveCoordinates() {

    fetch("/save-coordinates", {
        method: "POST"
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "saved") {
            alert("Coordinates saved!");
        }
    });
}