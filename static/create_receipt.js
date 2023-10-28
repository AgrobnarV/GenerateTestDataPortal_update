$(function () {
  var date = new Date();
  $("#paymentId").val(uuidv4());
  $("#receiptId").val(uuidv4());
  $("#CreatedData").val(date.toISOString());
  $("#UpdatedData").val(date.toISOString());
  $("#DoneDate").val(date.toISOString());
  $("#paymentBody").val('[{"name": "test", "sum": {"value": "1211.0"}}]');

  // Validate the form before submitting it
  $("#btn").click(async function () {
    axios.post("createReceipt", {
      payment_id: $("#paymentId").val(),
      receipt_id: $("#receiptId").val(),
      created_date: $("#CreatedDate").val(),
      updated_date: $("#UpdatedDate").val(),
      done_date: $("#DoneDate").val(),
      cancellation_date: $("#CancellationDate").val(),
      salary_type: $("#salaryType").val(),
      receipt_link: $("#receiptLink").val(),
      payment_body: $("#paymentBody").val(),
    })
      .then(function (response) {
        // The request was successful
        document.getElementById('log').innerHTML = `<span> Check created: ${JSON.stringify(response.data)}</span><br>`;
        document.getElementById('btn').disabled = false;
        notifyMe();
      })
      .catch(function (error) {
        // The request failed
        if (error.response && error.response.status === 408) {
          // Timeout
          document.getElementById('log').innerHTML = `<span>Long time no answer, check again</span><br>`;
          document.getElementById('btn').disabled = false;
          notifyMeN();
        } else {
          // Other error
          document.getElementById('log').innerHTML = `<span>Error ${decodeURIComponent(error.response.data.message)}</span><br>`;
          document.getElementById('btn').disabled = false;
          notifyMeN();
        }
      });
  });
});