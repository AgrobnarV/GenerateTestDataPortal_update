$(function () {
  $("#btn").click(async function () {
    document.getElementById('btn').disabled = true;
    document.getElementById('log').innerHTML = `Generate is coming <div class="spinner-border spinner-border-sm text-danger" role="status"/>`;

    // Make a fetch request to the create_special_boxes endpoint
    const response = await fetch("3st_service_create_tasks", {
      method: "GET",
      timeout: 60000,
      headers: {
        "Content-Type": "application/json",
      },
      body: new Blob([JSON.stringify({
        client_id: $("#client").val(),
        local_warehouse_id: $("#local_warehouse_id").val(),
        type_id: $("#type_id").val(),
        warehouse_place_id: $("#warehouse_place_id").val(),
        box_count: $("#box_count").val()
      })]),
    });

    // Check the response status code
    if (!response.ok) {
      console.error(response.statusText);
      document.getElementById('log').innerHTML = `<span>Error: ${response.statusText}</span><br>`;
      document.getElementById('btn').disabled = false;
      notifyMeN();
      return;
    }

    // The request was successful, so parse the response data
    const data = await response.json();

    // Update the UI with the response data
    document.getElementById('log').innerHTML = `<span>Task is created ${JSON.stringify(data)}</span><br>`;
    document.getElementById('btn').disabled = false;
    notifyMe();
  });
});
