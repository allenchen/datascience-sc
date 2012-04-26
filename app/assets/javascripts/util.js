$(function(){
  $('a').each(function(){
    if( this.host && this.host != location.host ) {
      $(this).attr('target', '_blank');
    }
  });
});
