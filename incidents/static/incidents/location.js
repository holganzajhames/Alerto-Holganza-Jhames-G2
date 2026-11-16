const capture = document.querySelector("#capture-gps");
const feedback = document.querySelector("#gps-status");

capture.addEventListener("click", () => {
  if (!navigator.geolocation) {
    feedback.textContent = "GPS is unavailable. You can still submit with the campus location.";
    return;
  }

  capture.disabled = true;
  feedback.textContent = "Getting your location…";
  navigator.geolocation.getCurrentPosition(({ coords }) => {
    document.querySelector("#id_latitude").value = coords.latitude.toFixed(6);
    document.querySelector("#id_longitude").value = coords.longitude.toFixed(6);
    document.querySelector("#id_location_accuracy_m").value = coords.accuracy.toFixed(2);
    feedback.textContent = "Approximate GPS coordinates added.";
    capture.disabled = false;
  }, () => {
    feedback.textContent = "GPS could not be captured. Enter the campus location to continue.";
    capture.disabled = false;
  }, { timeout: 10000 });
});
