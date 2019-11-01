const axios = require('axios');

async function makeGetRequest(code) {

  let url= 'http://192.168.56.1:5000/tag?tag='+ code;
  let res = await axios.get(url);

  let data = res.data;
  let headers = res.headers['set-cookie'][0];
  let cookie = headers.split(";")[0];

  return (data, cookie);
}

async function makePostRequest(resposta, session) {

    let dados = {
      'Content-Type': 'application/json',
      'Cookie': session
    }
    params = {resposta: resposta}

    let res = await axios.post('http://192.168.56.1:5000/tag', params, {headers: dados});    
    let pergunta = res.data;

    return pergunta;
}

 //makePostRequest('Python', 'session=.eJyVVFtv2jAU_itnfs4QkHJ9mVQxaZXWbZr6Mq19MMlJclTHTm0DRRX_fceGUqBBrFIeopzLd_EXvwhFzksx_fsiCukrtGLaTQTlYjpKxNMCnSejxVTMDKzNAh61WQG3QWNNaWVdky5BSV0uZIkO5qjM6otIhEXXGF7sePR38sNoTH6tfcWrEuGM9WLa2yTvIMdtkJVcYsRVmJcIpoAcXWap8cQFxvCsgDIHUudAukCL2pNUB6VTRpEP_NRqfWags6u2I3WSa-OrvZJ-i5LJkZJvQULQgku0IJtGEeaQSy_ZR2xkaAOPWaUpTIE3gM-NMhajqNjD73GgMBZqk6Ni5091_UHHXu-JpS3Eet0jZjceyIGiR4ynGhFcRsEQ5x04uU5ioQ5cnhZSkV-Dp3orxzXI9DKFUocchOlt-xy9Z6UUtn8CPsiYm7h93_2m94KMqzYZvbPpvJVZRRrhO0p7AhSFXkAbHKIFmAjXP4K7F7MghZ0LYjWuwJDq3Av4DHf84WtmtKnZwA4cEqt3xNQrsdcgkIZrKiHuRL0ka3TNJ3DJl3am6VljZojN3pUP7U53u6-Odt9VbAA_K24KQQ2ZRRsDlVOx_a2gsKYONf4DLF8R4d4o0DneINWxPagd1nOF_5vuQVssBu_Vr7br7_DZwy19LHrDzUMijM2xjhBuy_xmxp3DeTFOx4VMi95kMpH5KCuywTBPR91JP-1maT7EXq8_7r9deInwsuTJ8MlbUlW4dh82_wC1FtwQ.XbuoiA.Sz5XQNUHcDJxm1FG6ZttUB9CFmM');