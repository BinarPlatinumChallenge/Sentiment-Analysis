$(function(){

  $('#model').on('change', function(e) {
    let model = ($(this).val())
    if (model === 'NN') $('#feature-extraction-option').removeClass('hide')
    else $('#feature-extraction-option').addClass('hide')
  })

  $('#predict-button').on('click', function(e){
    e.preventDefault()
    text = $('#input_text').val()
    model = $('#model').val()
    feature_extraction = $('#feature_extraction').val()
    let data = {"text": text, "model": model, 'feature_extraction': feature_extraction}
    $.ajax({
      type: 'POST',
      url: '/sentiment',
      data : data,
      success : (data) => {
          const {text, sentiment} = data
          $('#result').removeClass('hide')
          $('#result-text').text(text)
          $('#result-model').text(model)
          $('#result-sentiment').text(sentiment)
          if (model === 'NN') {
            $('#feature-extraction-row').removeClass('hide')
            $('#result-feature-extraction').text(feature_extraction)
          } else {
            $('#feature-extraction-row').addClass('hide')
            $('#result-feature-extraction').text('')
          }
      },
      error : (data) => {
          console.log(data)
      }
    })
  })
})