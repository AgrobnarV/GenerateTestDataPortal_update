$(function () {
  $("#btn").click( async function () {
    document.getElementById('btn').disabled = true;
    document.getElementById('log').innerHTML = `Generate is coming <div class="spinner-border spinner-border-sm text-danger" role="status"/>`;

    const mlId = document.getElementById('route_list_id').value;
    const response = await fetch('load_route_list', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ids: route_list_id }),
    });

    // Check the response status code
    if (!response.ok) {
      throw new Error(await response.text());
    }

    // The request was successful, so parse the response data
    const data = await response.json();
    document.getElementById('log').innerHTML = `<span>Route list is loaded: ${JSON.stringify(data)}</span><br>`;
    document.getElementById('btn').disabled = false;
    notifyMe();
    if (error.status === 408) {
      document.getElementById('log').innerHTML = `<span>Long time no answer, load again.</span><br>`;
      document.getElementById('btn').disabled = false;
      notifyMeN();
    } else {
      document.getElementById('log').innerHTML = `<span>Error: ${error.message}</span><br>`;
      document.getElementById('btn').disabled = false;
      notifyMeN();
    }
  }
})
})
