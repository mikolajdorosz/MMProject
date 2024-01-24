// signup
if (location.pathname.includes("signup")) {
	const formFields = document.querySelectorAll("input");
	formFields[1].placeholder = "Username";
	formFields[2].placeholder = "Email";
	formFields[3].placeholder = "Password";
	formFields[4].placeholder = "Repeat password";
}

// add face camera

if (location.pathname.includes("add_face")) {
	const formFields = document.querySelectorAll("input");
	formFields[1].placeholder = "Name your face";

	const startWebcam = (e) => {
		e.preventDefault();
		navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
			const video = document.createElement("video");
			document.querySelector("#camera-container").prepend(video);
			video.srcObject = stream;
			video.play();

			document.querySelector("#camera-img").style.display = "none";
			document.querySelector("#start").style.display = "none";
			document.querySelector("#take-picture").style.display = "block";
			document.querySelector("#refresh").style.display = "block";

			const capture = () => {
				const canvas = document.createElement("canvas");
				document.querySelector("#camera-container").prepend(canvas);
				const context = canvas.getContext("2d");
				canvas.width = video.videoWidth;
				canvas.height = video.videoHeight;
				context.drawImage(
					video,
					0,
					0,
					video.videoWidth,
					video.videoHeight
				);
				canvas.toBlob((blob) => {
					const downloadLink = document.createElement("a");
					downloadLink.href = URL.createObjectURL(blob);
					downloadLink.download = "image.jpg";

					// Trigger a click on the link to prompt the download
					downloadLink.click();

					// Clean up
					URL.revokeObjectURL(downloadLink.href);
				}, "image/jpeg");
			};

			document
				.querySelector("#take-picture")
				.addEventListener("click", (e) => {
					e.preventDefault();
					video.style.display = "None";
					capture();
				});
		});
	};
	document.querySelector("#start").addEventListener("click", startWebcam);
	document.querySelector("#refresh").addEventListener("click", (e) => {
		e.preventDefault();
		location.reload();
	});
}
