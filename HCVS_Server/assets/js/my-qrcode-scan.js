        //闪光灯检测
    let scanner = "";
    let camList = [];
    let selectedCam = 0;
    const flashToggle = document.getElementById('flash-toggle');
    const flashState = document.getElementById('flash-state');
    const switchCamera = document.getElementById('switch-camera');
    const updateFlashAvailability = () => {
        scanner.hasFlash().then(hasFlash => {
            flashToggle.style.display = hasFlash ? 'inline-block' : 'none';
        });
    };
    flashToggle.addEventListener('click', () => {
        scanner.toggleFlash().then(() => {
          flashState.textContent = scanner.isFlashOn() ? 'On' : 'Off';
          if (scanner.isFlashOn()) {
                flashToggle.classList.remove('am-btn-danger');
                flashToggle.classList.add('am-btn-secondary');
          } else {
              flashToggle.classList.add('am-btn-danger');
              flashToggle.classList.remove('am-btn-secondary');
          }
        });
    });
    switchCamera.addEventListener('click', () => {
        selectedCam = (selectedCam + 1) % camList.length;
        console.log(camList[selectedCam]);
        console.log(camList);

        scanner.setCamera(camList[selectedCam]).then(updateFlashAvailability);
    });
function startScan(){
    const qrVideo = document.getElementById('qr-video');

    $('#qr-video').show();
    $('#video-control').show();

    let btnScan = $('#btn-scan');
    btnScan.text('Stop Scan');
    btnScan.attr('onclick', 'stopScan()');
    scanner = new QrScanner(qrVideo, result => setResult(result), {
        highlightScanRegion: true,
        highlightCodeOutline: true,
    });
    scanner.start().then(() => {
        updateFlashAvailability();
        // List cameras after the scanner started to avoid listCamera's stream and the scanner's stream being requested
        // at the same time which can result in listCamera's unconstrained stream also being offered to the scanner.
        // Note that we can also start the scanner after listCameras, we just have it this way around in the demo to
        // start the scanner earlier.
        QrScanner.listCameras(true).then(cameras => cameras.forEach(camera => {
            camList.push(camera.id);
        }));
    });

}
function stopScan(){
    scanner.stop();
    $('#qr-video').hide();
    $('#video-control').hide();
    let btnScan = $('#btn-scan');
    btnScan.text('Login By Scan QR Code');
    btnScan.attr('onclick', 'startScan()');
}