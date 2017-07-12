$(document).ready(function () {
    $('#callsign').focus();
    $('#location').focusout(
      function () {
        console.log("event fired");
        console.log("textarea value is " + $("#location").val());
        if ($("#location").val() == "") {
          $.ajax({
            url: "/operators/last/" + $("#callsign").val(),
            success: function (response) {
              $("#location").val(response);
            }
          });
        }
      }
    );
});

function form_prepop(call,ctype) {
    $("#callsign").val(call);
    $("#checkin_type").val(ctype);
    $("#notes").focus();
    $.ajax({
      url: "/operators/last/" + call,
      success: function (response) {
        $("#location").val(response);
      }
    });
};



{% for c in net.checkedin_operators() %}
{% set op_call = c.Operator.call %}

$("#{{ op_call }}_recheck").click(function () {
    form_prepop("{{ op_call }}", "ReCheck");
});

$("#{{ op_call }}_wxreport").click(function () {
    form_prepop("{{ op_call }}", "WXReport");
});

$("#{{ op_call }}_checkout").click(function () {
    form_prepop("{{ op_call }}", "CheckOut");
});

{% endfor %}
