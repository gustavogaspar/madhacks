const axios = require('axios');

async function makeGetRequest(code) {

  let url= 'http://132.145.163.158:5000/tag?tag='+ code;
  let res = await axios.get(url, {withCredentials: true});

  let data = res.data;
  let headers = res.headers['set-cookie'][0];
  let cookie = headers.split(";")[0];
  data.sessionid = cookie;
  console.log(data)
  return data;
}

makeGetRequest(6)

async function makePostRequest(resposta, session) {

    let dados = {
      'Content-Type': 'application/json',
      'Cookie': session
    }
    params = {resposta: resposta}
    console.log(dados)

    let res = await axios.post('http://132.145.163.158:5000/tag', params, {headers: dados});    
    let pergunta = res.data;
    console.log(pergunta)
    return pergunta;
}

 //makePostRequest('Yes', 'session=.eJx9ksFOwzAQRH_F8tmHJi1JyQVBy6ECAYJKCCEOjrNprDreknUoVdV_ZxMEVavCKdJmPPM83q10loKW2etWljpU0MhsoKQtZJYo-d4CBYteZnKKYoOtqPQHCO03grQDEvC5gsaCN3AhlWyAVshuxPoXIHWHPCRsgsyindoHRN8B0WHCc2VNJbAULBIlOodr6xeCltY5EsV3_tLj-jhqgnXdemt0ZySeer26gwUGezC6wlCpGTv5IG7Y5xcuPgWXnrp-rSlA0xMGXFlDIocO9BjpkpZizqJH0E5MWgpY87EHbT2pWy4cfHe1Ofain_9_Aw5PAY4PAC9zbMNhdfTT3bpvtti_4DHuNX9zXoRKTBoobG6dDRs186Vr-W071Psu-58KR7s3JbEpoO73h4CIuWZTNjdFGiVREpv8LB0kcWyis_I8Kkd5ypN4qMej1EA8MvtdUTLoBZ9MeBQa66puP992X0B95I4.XcCqwQ.WLQ1XCDO97JtOe1-U3vMxpTuGdQ');