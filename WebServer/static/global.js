function tryLogin() {
    $.ajax({
        type : 'GET',
        url : "/tryLogin",
        data : {},
        success: tryLoginCallback
    });
}

function tryLoginCallback(result) {
    if(result.error == 0) {
        /* Redirect */
        window.location.href = "dash";
    }
}

function loginFunction() {
    username  = $("#username_field").val();
    passwd = $("#password_field").val();
    $.ajax({
        type : 'POST',
        url : "/doLogin/",
        data : {'username': username, 'passwd': passwd},
        success: loginCallback
    });
}

function loginCallback(result) {
    /* If we had a result, and the error is not 0 */
    if(result.error != 0) {
        $("#username_info").attr("data-error", result.message);
        $("#password_info").attr("data-error", result.message);
        $("#username_field").addClass("invalid");
        $("#password_field").addClass("invalid");
    }
    else {
        /* Redirect */
        window.location.href = "dash";
    }
}

function initLoginBox() {

    $("#username_field").on('input',function(e){
        $("#username_info").attr("data-error", "");
        $("#username_field").removeClass("invalid");
    });

    $("#password_field").on('input',function(e){
        $("#password_info").attr("data-error", "");
        $("#password_field").removeClass("invalid");
    });

    /* Set aestetic login box */
    $('input').blur(function() {
        var $this = $(this);
        if ($this.val())
          $this.addClass('used');
        else
          $this.removeClass('used');
    });

    var $ripples = $('.ripples');

    $ripples.on('click.Ripples', function(e) {

        var $this = $(this);
        var $offset = $this.parent().offset();
        var $circle = $this.find('.ripplesCircle');

        var x = e.pageX - $offset.left;
        var y = e.pageY - $offset.top;

        $circle.css({
            top: y + 'px',
            left: x + 'px'
        });

        $this.addClass('is-active');

    });

    $ripples.on('animationend webkitAnimationEnd mozAnimationEnd oanimationend MSAnimationEnd', function(e) {
        $(this).removeClass('is-active');
    });

    /* Set auto submit on enter */
    $('#login_submit').keydown(function(event) {
        if (event.which === 13)  {
            event.preventDefault();
            loginFunction();
        }
    });
    $("#username_field").keydown(function(event) {
        if (event.which === 13)  {
            event.preventDefault();
            loginFunction();
        }
    });
    $("#password_field").keydown(function(event) {
        if (event.which === 13)  {
            event.preventDefault();
            loginFunction();
        }
    });
    $("#login_btn").click(loginFunction);
}