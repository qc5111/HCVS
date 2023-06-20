//AES
function hexToUint8Array(hexString) {
    // 将十六进制字符串转换为 Uint8Array
    const uint8Array = new Uint8Array(hexString.length / 2);
    for (let i = 0; i < hexString.length; i += 2) {
        const byte = parseInt(hexString.substr(i, 2), 16);
        uint8Array[i / 2] = byte;
}

return uint8Array;
}
// 加密函数
function encryptAES256(plaintext, key) {
  if (key == null) {
    key = window.crypto.getRandomValues(new Uint8Array(48));
  }
  let iv = CryptoJS.lib.WordArray.create(key.slice(0, 16));
  let aesKey = CryptoJS.lib.WordArray.create(key.slice(16, 48));
  let plaintext2 = CryptoJS.lib.WordArray.create(plaintext);
  let encrypted = CryptoJS.AES.encrypt(
      plaintext2,
      aesKey,
      {
          iv: iv,
          padding: CryptoJS.pad.NoPadding
      }
  );
  const decodedData = atob(encrypted.toString());

  // 将解码后的字符串转换为 Uint8Array
  const enData = new Uint8Array(decodedData.length);
  for (let i = 0; i < decodedData.length; i++) {
    enData[i] = decodedData.charCodeAt(i);
  }
  //console.log(enData);
  return {key, enData};
}

// 解密函数
function decryptAES256(key, ciphertext) {
    // 导入密钥材料
  let iv = CryptoJS.lib.WordArray.create(key.slice(0, 16));
  let aesKey = CryptoJS.lib.WordArray.create(key.slice(16, 48));
  //加密文本转换为base64
    let ciphertext2 = CryptoJS.enc.Base64.stringify(CryptoJS.lib.WordArray.create(ciphertext));
    let decrypted = CryptoJS.AES.decrypt(
        ciphertext2,
        aesKey,
        {
            iv: iv,
            padding: CryptoJS.pad.NoPadding
        }
    );
    return hexToUint8Array(decrypted.toString());

}
//ECC
function ecc_key_to_pkcs8(private_key_raw, public_key_raw){
  const privateKeyHead = new Uint8Array([
  0x30, 0x81, 0x87, 0x02, 0x01, 0x00, 0x30, 0x13, 0x06, 0x07, 0x2a, 0x86, 0x48, 0xce, 0x3d, 0x02, 0x01,
  0x06, 0x08, 0x2a, 0x86, 0x48, 0xce, 0x3d, 0x03, 0x01, 0x07, 0x04, 0x6d, 0x30, 0x6b, 0x02, 0x01, 0x01,
  0x04, 0x20
  ]);
  const privateKeyMiddle = new Uint8Array([0xa1, 0x44, 0x03, 0x42, 0x00, 0x04]);
  //拼接key
    let private_key = new Uint8Array(36+32+6+64);
    private_key.set(privateKeyHead);
    //加入private key
    private_key.set(private_key_raw,36);
    private_key.set(privateKeyMiddle,68);
    //加入public key
    private_key.set(public_key_raw,74);
    return private_key;
}
//ECC sign
async function ecc_sign2(private_key, data) {
  try {
    const privateCryptoKey = await crypto.subtle.importKey(
      "pkcs8",
      private_key.buffer,
      { name: "ECDSA", namedCurve: "P-256" },
      true,
      ["sign"]
    );

    const signature = await crypto.subtle.sign(
      {
        name: "ECDSA",
        hash: { name: "SHA-256" },
      },
      privateCryptoKey,
      data.buffer
    );
    return new Uint8Array(signature);
  } catch (error) {
    // 处理错误
    console.error(error);
    throw error;
  }
}
