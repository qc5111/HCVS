function setCookie(name, value, days) {
  var expires = "";
  if (days) {
    var date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + value + expires + "; path=/";
}

function intToBytes(int, length) {
  const bytes = new Uint8Array(length);
  for (let i = 0; i < length; i++) {
    bytes[length - 1 - i] = int & 0xff;
    int -= bytes[length - 1 - i];
    int /= 256;
  }
  return bytes;
}

function base64_to_Uint8Array(base64_string) {
    let decodedData = atob(base64_string);
    let bytes = new Uint8Array(decodedData.length);
    for (let i = 0; i < decodedData.length; i++) {
      bytes[i] = decodedData.charCodeAt(i);
    }
    return bytes;
}
function Uint8Array_to_base64(uint8Array) {
  // 将 Uint8Array 转换为字符串
  let binaryString = '';
  uint8Array.forEach(byte => {
    binaryString += String.fromCharCode(byte);
  });
  return btoa(binaryString).replace(/=/g, "");
}

function deCodeIdBytes(idBytes){
    let id = 0;
    for (let i = idBytes.length - 1; i >= 0; i--) {
      id = id+idBytes[i] * Math.pow(256,idBytes.length - 1 - i);
    }
    return id;
}

function deCodeQRCodeData(data){
    let bytes = base64_to_Uint8Array(data);
    // 切割ID与加密私钥
    let idBytes = bytes.slice(0, 6);
    let key = bytes.slice(6, 38);
    let id = deCodeIdBytes(idBytes);
    //base64编码idBytes，得到idStr
    return {id, key};
}

function timestampToDate(ts){
    let date = new Date(ts);
    return date.toLocaleString();
}