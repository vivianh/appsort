//...
 
obj.dd.on('click', function(event){
    $(this).toggleClass('active');
    console.log('uahsfha');
    return false;
});
 
//...
 
$(function() {
 
    var dd = new DropDown( $('#dd') );
 
    $(document).click(function() {
        // all dropdowns
        $('.wrapper-dropdown-1').removeClass('active');
    });
 
});
