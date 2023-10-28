import axios from 'axios';

document.getElementById('btn').addEventListener('click', setBoxAttributes);

async function setBoxAttributes() {
  const btn = document.getElementById('btn');
  const log = document.getElementById('log');

  btn.disabled = true;
  log.innerHTML = `Generate is coming <div class="spinner-border spinner-border-sm text-danger" role="status"/>`;

  try {
    const response = await axios.post('set_priority', {
      box_ids: document.getElementById('box_ids').value,
      adult: document.getElementById('adult').checked,
      alcohol: document.getElementById('alcohol').checked,
      by_door: document.getElementById('by_door').checked,
      premium: document.getElementById('premium').checked,
      jewelery: document.getElementById('jewelery').checked
    });

    log.innerHTML = `<span>Attributes are filled: ${JSON.stringify(response.data)}</span><br>`;
    notifyMe();
  } catch (error) {
    if (error.response && error.response.status === 408) {
      log.innerHTML = `<span>Long time no answer, set again</span><br>`;
      notifyMeN();
    } else {
      const error_resp = unescape(new TextDecoder().decode(error.response.data)).replace(/["']/g, "");
      log.innerHTML = `<span>Error: ${decodeURIComponent(error_resp)}</span><br>`;
      notifyMeN();
    }
  } finally {
    btn.disabled = false;
  }
}