var prevElement = null;

function sendIndex(index, element) {

  if(prevElement != null) {
    var old_line = document.getElementById(prevElement);
    old_line.style.color = "black";
  }

  var line = document.getElementById(element);
  line.style.color = "pink";

  prevElement = element;

  $.ajax({
    
    url: '/dashboard/' + index,
    type: 'GET',
    success: function (data) {
      $('#selected-sentence').text(data.index + '.) ' + data.sentence);
    },
  });
}

$("form[name=signup_form").submit(function(e) {

  var $form = $(this);
  var $error = $form.find(".error");
  var data = $form.serialize();

  $.ajax({
    url: "/user/signup",
    type: "POST",
    data: data,
    dataType: "json",
    success: function(resp) {
      window.location.href = "/dashboard/";
    },
    error: function(resp) {
      $error.text(resp.responseJSON.error).removeClass("error--hidden");
    }
  });

  e.preventDefault();
});

$("form[name=login_form").submit(function(e) {

  var $form = $(this);
  var $error = $form.find(".error");
  var data = $form.serialize();

  $.ajax({
    url: "/user/login",
    type: "POST",
    data: data,
    dataType: "json",
    success: function(resp) {
      // Redirects to dashboard after succesful login
      window.location.href = "/dashboard/";
    },
    error: function(resp) {
      $error.text(resp.responseJSON.error).removeClass("error--hidden");
    }
  });

  e.preventDefault();
});
