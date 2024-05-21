// Global Variables

// Handles highlighting text
var prevElement = null;
var flag = false;

// Grabs user text and id from URL
const url_str = window.location.pathname;
const string_array = url_str.split("/")
const user_id = string_array[3];
const chapter_number = string_array[4];

//function openMenu(){
//   document.getElementById("navbarDropdownmenu").className="show";
//}

function showUserName(){
  document.getElementById("new-username").className="show";
  document.getElementById("usernameOK").className="show";
}

function updateUsername() {
    var newUsername = document.getElementById('new-username').value;
    if (newUsername) {
      $.ajax({
        url: '/joyce/update_username',
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        //data: {new_username: newUsername },
        data: JSON.stringify({ 'name': newUsername}),
        success: function(data) {
           alert('Username updated successfully');
        },
        error: function(xhr, status, error) {
            console.error('Error updating username:', error);
            alert('An error occurred while updating username');
        }
    });
    }
}

// This function removes the text from the database
function dropText(textName){

  var fileName = textName.split('_')[0];

  var confirmation = confirm("Are you sure you want to remove '" + fileName + "'?");

  if (confirmation) {
    $.ajax({
      url: '/joyce/dropText/'+ textName,
      type: 'POST',
      contentType: "application/json",
      success: function (data) {
        window.location.reload();
      },
    });
  } else {
    console.log("Removal cancelled.");
  }

}



function showPassword(){
  document.getElementById("new-password").className="show";
  document.getElementById("passwordOK").className="show";
}

function updatePassword() {
    var newPassword = document.getElementById('new-password').value;
    if (newPassword) {
      $.ajax({
        url: '/joyce/update_password',
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        //data: {new_username: newUsername },
        data: JSON.stringify({ 'password': newPassword}),
        success: function(data) {
           alert('password updated successfully');
        },
        error: function(xhr, status, error) {
            console.error('Error updating password:', error);
            alert('An error occurred while updating password');
        }
    });
    }
}


function setVisibleContent() {
  // window.alert("setVisibleContent() called")
  var visibleContent = localStorage.getItem('visible-content-' + user_id);
  if (visibleContent === 'categories') 
    showCategories();
  else if (visibleContent === 'search') 
    showSearch();
  else if (visibleContent === 'notes') 
    showNotes();
  else 
    showInspect(); // Default to "Inspect Sentence" if not set
}


function showInspect() {
  //window.alert("showInspect() called")
  document.getElementById('inspect-sentence').style.display = 'block';
  document.getElementById('categories').style.display = 'none';
  document.getElementById('search').style.display = 'none';
  document.getElementById('notes').style.display = 'none';
  localStorage.setItem('visible-content-' + user_id, 'inspect-sentence');
}


function showNotes() {
  //window.alert("showInspect() called")
  document.getElementById('inspect-sentence').style.display = 'none';
  document.getElementById('categories').style.display = 'none';
  document.getElementById('search').style.display = 'none';
  document.getElementById('notes').style.display = 'block';
  localStorage.setItem('visible-content-' + user_id, 'notes');
}

function showCategories() {
  //window.alert("showCategories() called")
  var selectElement = document.getElementById("dbDropdown");
   // Get the selected option
   var selectedOption = selectElement.options[selectElement.selectedIndex];
  
   // Get the value of the selected option
   var selectedValue = selectedOption.value;
  
  document.getElementById('inspect-sentence').style.display = 'none';
  document.getElementById('categories').style.display = 'block';
  document.getElementById('search').style.display = 'none';
  document.getElementById('notes').style.display = 'none';
  if (selectedValue == "Add Category") {
    document.getElementById('addcategoryButton').style.display = 'block';
    document.getElementById('removecategoryButton').style.display = 'block';
    $('#category-paragraph').text("");
  document.getElementById('addHighlight').style.display = 'none';
  document.getElementById('removeHighlight').style.display = 'none';
  document.getElementById('addText').style.display = 'none';
  document.getElementById('removeText').style.display = 'none';
  } else {
    document.getElementById('addcategoryButton').style.display = 'none';
    document.getElementById('removecategoryButton').style.display = 'none';
  }
  localStorage.setItem('visible-content-' + user_id, 'categories');
}

function showButtons() {
  var selectElement = document.getElementById("dbDropdown");
   // Get the selected option
   var selectedOption = selectElement.options[selectElement.selectedIndex];
  
   // Get the value of the selected option
   var selectedValue = selectedOption.value;
   
   var index = localStorage.getItem('index-' + user_id);
   
     
  if (selectedValue !== "Add Category"){
    document.getElementById('addcategoryButton').style.display = 'none';
    document.getElementById('removecategoryButton').style.display = 'none';
    document.getElementById('addHighlight').style.display = 'block';
    document.getElementById('removeHighlight').style.display = 'block';
    document.getElementById('addText').style.display = 'block';
    document.getElementById('removeText').style.display = 'block';
    $.ajax({

      url: "/joyce/updateCategories/" + index + "/" + selectedValue,
      type: 'GET',
      success: function (data) {
        $('#category-paragraph').text(data.categories);
      },
      // error: function(resp) {
      //   window.alert("Error")
      // }
    });
  } else {
    $('#category-paragraph').text("");
    document.getElementById('addcategoryButton').style.display = 'block';
    document.getElementById('removecategoryButton').style.display = 'block';
    document.getElementById('addHighlight').style.display = 'none';
    document.getElementById('removeHighlight').style.display = 'none';
    document.getElementById('addText').style.display = 'none';
    document.getElementById('removeText').style.display = 'none';
    
  }    
      
}

function showSearch() {
  //window.alert("showsearch() called")
  document.getElementById('inspect-sentence').style.display = 'none';
  document.getElementById('categories').style.display = 'none';
  document.getElementById('search').style.display = 'block';
  document.getElementById('notes').style.display = 'none';
  localStorage.setItem('visible-content-' + user_id, 'search');
}

function showKey(popup) {
  //window.alert("showKey() called")
  var status = document.getElementById(popup).style.display;
  if(status === 'none')
    document.getElementById(popup).style.display = 'block';
  else if(status === 'block')
    document.getElementById(popup).style.display = 'none';
}

function showKeyPopup(keyPopup, element) {
  //window.alert("showKeyPopup() called")
  var status = document.getElementById(keyPopup).style.display;
  if(status === 'none')
    document.getElementById(keyPopup).style.display = 'block';
  else if(status === 'block')
    document.getElementById(keyPopup).style.display = 'none';

  localStorage.setItem('current-id-' + user_id, element);
}

function closePopup(id) {
  //window.alert("closePopup() called")
  document.getElementById(id).style.display = 'none';
}



// These functions control the notes box in the 3rd column
function clearDefaultText() {
  var textarea = document.getElementById("notes-box");
  if (textarea.value === textarea.defaultValue) {
    textarea.value = '';
  }
}

function send_notes(index) {
  $.ajax({
    type: 'GET',
    url: '/joyce/getNotes/' + index,
    success: function(data) {
        $('#notes-content').val(data.notes);
    },
  });
}


// These functions control the text box edits and reads from DB
var column1 = document.getElementById("textDisplay");
if (column1) {

  $(document).ready(function(){

    function updateNotes() {
      var new_notes = $('#notes-content').val();
      $.ajax({
          type: 'POST',
          url: '/joyce/updateNotes',
          contentType: 'application/json',
          data: JSON.stringify({text: new_notes}),
          success: function(response) {
              console.log(response);
          },

      });
  }


    $('#notes-content').on('input', function() {
      updateNotes();
    });

  });
}

// end of notes functions


// Scroll restoration
// Check if the element with id "textDisplay" exists
var column1 = document.getElementById("textDisplay");

if (column1) {
  // Add scroll event listener
  column1.addEventListener("scroll", scrollFunction);
  
  // Restore scroll position on window reload
  window.addEventListener("load", loadScroll())

}

function loadScroll() {
  //var savedScrollPosition = localStorage.getItem("scrollPosition");
  
  $.ajax({
    url: "/joyce/getScrollProgress/",
    type: 'GET',
    success: function (data) {

        // window.alert("Load scroll " + data.scroll)
        if(data.scroll != null)
        {
          column1.scrollTop = data.scroll;
        }
    },
  });

};


function scrollFunction() {
  // Get the scroll position of the column1 div
  var winScroll = column1.scrollTop;
  // Get the total height of the content inside column1
  var height = column1.scrollHeight - column1.clientHeight;
  // Calculate scroll percentage
  var scrolled = (winScroll / height) * 100;
  

  // Update the scroll progress in our text attributes document
  $.ajax({
    url: '/joyce/sendScrollProgress/',
    type: 'POST',
    contentType: "application/json",
    data: JSON.stringify({'scroll': winScroll}),
    success: function (data) {
      // window.alert(scrolled)
    },
  });

  // Log scroll percent
  console.log("Percentage scrolled:", scrolled);
  //localStorage.setItem("scrollPosition", winScroll);

}
// end of scroll restoration functions


function get_key_text(e) {
  var current_key_id = localStorage.getItem('current-id-' + user_id);
  var form = document.getElementById("key-input").value;
  if(form.length < 0 || form.length > 10) {
    window.alert("Please enter a valid name less than 10 characters.")
  }
  else {

    $.ajax({
      url: "/joyce/updateKeyText/",
      type: 'POST',
      contentType: "application/json",
      data: JSON.stringify({'text': form, 'current_id': current_key_id}),
      success: function (data) {
        //window.alert("get_key_text(e) called successfully.")
      },
    });
    location.reload();
  }
}


function updateKeyColor(value, element) {
  $.ajax({
    url: "/joyce/updateKeyColor/",
    type: 'POST',
    contentType: "application/json",
    data: JSON.stringify({'color': value, 'current_id': element}),
    success: function (data) {
      //window.alert("updateKeyColor called successfully.")
    },
  });
}
function change_color(colorPosition, name) {
  //send_color_to_server(color);
  ///localStorage.setItem('color-' + user_id, color);
  //localStorage.setItem('color_name-' + user_id, name);

  $.ajax({
    url: "/joyce/getColorList/" + colorPosition,
    type: 'GET',
    success: function (data) {

        document.getElementById("color-picker-label").innerHTML = "Now highlighting with color " + name;
        document.getElementById("color-picker").value = data.dbColor;
        localStorage.setItem('color_name-'+ user_id, name);
    },
  });
}

function send_categoryData(index) {
  var selectElement = document.getElementById("dbDropdown");
    
    // Get the selected option
    var selectedOption = selectElement.options[selectElement.selectedIndex];
    
    // Get the value of the selected option
    var selectedValue = selectedOption.value;
  $.ajax({

    url: "/joyce/updateCategories/" + index + "/" + selectedValue,
    type: 'GET',
    success: function (data) {
      $('#category-paragraph').text(data.categories);
    },
  });
}


function sendIndex(fileName, chapter, index, element) {
  if (prevElement !== null) {
    var old_line = document.getElementById(prevElement);
    var spans = old_line.getElementsByTagName("span");
    for (var i = 0; i < spans.length; i++) {
        spans[i].style.textShadow = "none";
    }
  }

  var line = document.getElementById(element);
  var childSpans = line.getElementsByTagName("span");
  for (var i = 0; i < childSpans.length; i++) {
      childSpans[i].style.textShadow = "1px 0 black";
  }

  prevElement = element;

  $.ajax({
    url: '/joyce/dashboard/' + fileName + "/" + chapter + "/" + index,
    type: 'GET',
    success: function (data) {
      $('#selected-sentence').text(data.index + '.) ' + data.sentence);

      // data.index is subtracted by one to correct database indexing from display
      // indexing
      send_notes(data.index-1);
      send_categoryData(data.index-1);

      localStorage.setItem('file-name-' + user_id, fileName);
      localStorage.setItem('chapter-' + user_id, chapter);
      localStorage.setItem('index-' + user_id, index);
    },
  });
}

// Only call sendIndexHighlight when on dashboard
window.onload = function (){
  var column1 = document.getElementById("textDisplay");
  if (column1) {
    sendIndexHighlight();
  }
}

function sendIndexHighlight(){

  fileName = string_array[3]
  chapter = string_array[4]

  var color_name = localStorage.getItem('color_name-' + user_id);

  $.ajax({
    url: "/joyce/getIndex/",
    type: 'GET',
    success: function (dataIndex) {

      //window.alert("Index retreived from DB: " + data.lastIndex)
      index = dataIndex.lastIndex

      $.ajax({
        url: '/joyce/dashboard/' + fileName + '/' + chapter + '/' + index,
        type: 'GET',
        success: function (data) {
          //window.alert("Sucessful call in sendIndexHighlight().")
          $('#selected-sentence').text(data.index + '.) ' + data.sentence);
          $("#color-picker-label").text("Now highlighting with " + color_name);
          
          // data.index is subtracted by one to correct database indexing from display
          // indexing
          send_categoryData(data.index-1);
          send_notes(data.index-1);
        },
      });

    },
  });
   
}


// when user clicks on a text in table they are redirected to the correct text and the last chapter accessed
function sendTable(table_name) {

  //window.alert(table_name);
  localStorage.setItem('current-file', table_name);

  $.ajax({
    url: '/joyce/collectionInfo/' + table_name,
    type: 'GET',
    success: function (data) {
      currentChapter = data.chapter
      // window.alert(currentChapter)
      window.location.href = "/joyce/dashboard/" + table_name + "/" + currentChapter;
    },
  });

}

function navigateChapter(offset, fileName, currentChapter, numberOfChapters) {

  var newChapter = currentChapter*1 + offset*1;
  // new chapter is within bounds
  if (newChapter >= 1 && newChapter <= numberOfChapters ) {
    window.location.href = "/joyce/dashboard/" + fileName + "/" + newChapter;
  }
}

// Handles highlighting of text in column2 of 
// webpage

$(document).ready(function() {

  $('.dashcol2').on('mouseup', function() {
    var highlightedText = getHighlightedText();
    sendHighlightedTextToServer(highlightedText);
  });
 
  function getHighlightedText() {
    var selection = window.getSelection();
    var parentElement = selection.anchorNode.parentElement;
    
    if (parentElement && parentElement.id === "selected-sentence") {
        if (selection.rangeCount > 0) {
            var range = selection.getRangeAt(0);
            
            skipIndex(range);
            expandRangeToWords(range);

            var fragment = range.cloneContents();

            var tempDiv = document.createElement('div');
            tempDiv.appendChild(fragment);

            var text = tempDiv.innerText || tempDiv.textContent;

            // Check if the text is equal to a single space,
            // and return a string to alert the user
            if (text.trim() === '')
                return "Highlight text to continue.";

            return text;
        }
    }
    return "Highlight text to continue.";
  } 
  
  function skipIndex(range) {
    var startContainer = range.startContainer;
    var startOffset = range.startOffset;
  
    // Regular exp. for #.), where # is any number
    var match = startContainer.textContent.match(/^\d+\.\)\s/);
  
    if (match && startOffset < match[0].length) {
      
      // Move range to end of length of match + 1 for ) 
      range.setStart(startContainer, match[0].length+1);

    }
  }
  
  function expandRangeToWords(range) {

    // Expand the start of the range to the beginning of the word
    while (!isValidChar(range.startContainer.textContent[range.startOffset - 1]) && range.startOffset > 0) {
      range.setStart(range.startContainer, range.startOffset - 1);
    }
  
    // Expand the end of the range to the end of the word
    while (!isValidChar(range.endContainer.textContent[range.endOffset]) && range.endOffset < range.endContainer.length) {
      range.setEnd(range.endContainer, range.endOffset + 1);
    }
    
  }
  
  function isValidChar(char) {

    // Checks if the character is not a whitespace or quotation
    return /\s/.test(char);

  }
 

  function sendHighlightedTextToServer(text) {

    //var color = document.getElementById("color-picker").value;
    //window.alert('Sendhighlightedtext called.')

    $.ajax({
      type: 'POST',
      url: '/joyce/highlight/',
      contentType: 'application/json;charset=UTF-8',
      data: JSON.stringify({ 'highlightedText': text }),
      success: function(resp) {
        //window.alert(resp.displayedText);
        var visibleContent = localStorage.getItem('visible-content-' + user_id);
        // Sends to inspect sentence tab
        if(visibleContent == 'inspect-sentence'){
          $('#highlightText').text(resp.displayedText);
        }
        // Sends to search tab
        else if (visibleContent == 'search') {
          document.getElementById('search-box').value = resp.displayedText; 
          // $('#submit-box').value(resp.displayedText);
        }
        localStorage.setItem('phrase-' + user_id, text);
      },
      error: function(error) {
        console.error('Error:', error);
      }
    });
  }

});

function saveCheckboxState() {
  var checkbox = document.querySelector('.switch-highlight');
  localStorage.setItem('checkboxState', checkbox.checked);
}

// Function to load the checkbox state from localStorage
function loadCheckboxState() {
  var checkbox = document.querySelector('.switch-highlight');
  var checkboxState = localStorage.getItem('checkboxState');
  if (checkboxState === 'true') {
    checkbox.checked = true;
  } else {
    checkbox.checked = false;
  }
}

if (column1) {
  document.addEventListener("DOMContentLoaded", loadCheckboxState);
  document.querySelector('.switch-highlight').addEventListener('change', saveCheckboxState);
}

function highlight() {
  //window.alert("Highlight() called.")
  var checkbox = document.querySelector('.switch-highlight'); 
  if (checkbox.checked) {
    highlight_background();
  } else {
    highlight_text();
  }
}

function submitSearch() {
  var target = document.getElementById("search-box").value;
  searchText(target)
}


var searchbox = document.getElementById('search');
if (searchbox) {
  function searchText(target) {
    $.ajax({
      url: "/joyce/searchText/" + target,
      type: 'POST',
      contentType: "application/json",
      data: JSON.stringify({'fileName': user_id, 'chapter': chapter_number}),
      success: function (data) {
        //window.alert("searchText called successfully.")
        $('#search-results').text(data.results);
        if (data.sentences) {
          var sentenceContainer = $('#selected-sentence');
          sentenceContainer.empty();
          data.sentences.forEach(function(sentence) {
          sentenceContainer.append('<p id=\'selected-sentence\'>' + sentence + '</p>');
          });
      }
        $('#sentence').text(data.sentences);

      },
    });
  }
}
function addHighlightText() {
  var selectElement = document.getElementById("dbDropdown");
  // Get the selected option
  var selectedOption = selectElement.options[selectElement.selectedIndex];
  
  // Get the value of the selected option
  var selectedValue = selectedOption.value;
  $.ajax({
    url: "/joyce/addTextCat/",
    type: "POST",
    data: {cat: selectedValue},
    success: function(data) {
      
      location.reload();   
    }
  });
}
function removeHighlightText() {
  var selectElement = document.getElementById("dbDropdown");
  // Get the selected option
  var selectedOption = selectElement.options[selectElement.selectedIndex];
  
  // Get the value of the selected option
  var selectedValue = selectedOption.value;


  $.ajax({
    url: "/joyce/removeTextCat/",
    type: "POST",
    data: {cat: selectedValue},
    success: function(data) {
      
      location.reload();   
    }
  });
}

function submitText() {
  var textarea = document.getElementById("catText2");
  var selectElement = document.getElementById("dbDropdown");
    
  // Get the selected option
  var selectedOption = selectElement.options[selectElement.selectedIndex];
  
  // Get the value of the selected option
  var selectedValue = selectedOption.value;
  
  // Do something with the selected value
  console.log(selectedValue);
    
  var value = textarea.value;
  
  $.ajax({
    url: "/joyce/addSubmitText/",
    type: "POST",
    data: { text: value, cat: selectedValue }, 
    success: function(data) {
      
      location.reload(); 
    }
  });
}

function submitNewCategory() {
  var textarea = document.getElementById("catText2");
  var value = textarea.value;
  console.log("Value from textarea:", value);
  $.ajax({
    url: "/joyce/addCategory/",
    type: "POST",
    data: { text: value }, 
    success: function(data) {
      
      location.reload(); 
    }
  });
}

function removeCategory() {
  var textarea = document.getElementById("catText2");
  var value = textarea.value;
  console.log("Value from textarea:", value);
  $.ajax({
    url: "/joyce/removeCategory/",
    type: "POST",
    data: { text: value }, 
    success: function(data) {
      
      location.reload(); 
    }
  });
}

function removeText() {
  var textarea = document.getElementById("catText2");
  var selectElement = document.getElementById("dbDropdown");
    
    
    var selectedOption = selectElement.options[selectElement.selectedIndex];
    
    
    var selectedValue = selectedOption.value;
    
  var value = textarea.value;
  $.ajax({
    url: "/joyce/removeSubmitText/",
    type: "POST",
    data: { text: value, cat: selectedValue }, 
    success: function(data) {
      
      location.reload(); 
    }
  });
}
if (column1) {
  $(document).ready(function() {
    // Fetch data from MongoDB
    $.ajax({
        url: "/joyce/getMongoData",
        type: "GET",
        success: function(data) {
            // Populate dropdown with MongoDB data
            var dropdown = $("#dbDropdown");
            dropdown.empty(); // Clear dropdown
            dropdown.append($("<option></option>").attr("value", "Add Category").text("Modify Categories"));
            $.each(data, function(index, value) {
                dropdown.append($("<option></option>").attr("value", value).text(value));
            });
        }
    });
  });
}

function highlight_text() {
  //window.alert('highlight_text() called.')
  var color = document.getElementById("color-picker").value;

  $.ajax({
    url: "/joyce/submitHighlight/",
    type: "POST",
    data: JSON.stringify({ 'color': color }),
    success: function(data) {
      //window.alert("highlight() called with " + color);
      location.reload();   
    }
  });
}

function highlight_background() {
  //window.alert('highlight_background() called.')
  var color = document.getElementById("color-picker").value;

  $.ajax({
    url: "/joyce/highlightBackground/",
    type: "POST",
    data: JSON.stringify({ 'color': color }),
    success: function(data) {
      //window.alert("highlight_background() called with " + color);
      location.reload();   
    }
  });
}

function send_color_to_server(color) {
  $.ajax({
    url: "/joyce/sendColor/",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({'color': color }),
    success: function(data) {
      //window.alert("send_color_to_server() called with " + color)
    }
  });
}

function send_color(value) {
  // window.alert("send_color() called with " + value, label)
  
  send_color_to_server(value);

  localStorage.setItem('color-' + user_id, value);
  localStorage.setItem('color_name-' + user_id, value);

  document.getElementById("color-picker-label").innerHTML = "Now highlighting with color " + localStorage.getItem('color_name-' + user_id);
}

//
//////////////////////////////////////////////////////////////////////////////////
//

$("form[name=signup_form").submit(function(e) {

  e.preventDefault();

  var $form = $(this);
  var $error = $form.find(".error");
  var data = $form.serialize();


  $.ajax({
    url: "/joyce/user/signup/",
    type: "POST",
    data: data,
    dataType: "json",
    success: function(resp) {
      // Redirects to upload page since it is first login
      window.location.href = "/joyce/loader/";
    },
    error: function(resp) {
      //window.alert("Error")
    }
  });


});

$("form[name=login_form").submit(function(e) {

  var $form = $(this);
  var $error = $form.find(".error");
  var data = $form.serialize();

  $.ajax({
    url: "/joyce/user/login",
    type: "POST",
    data: data,
    dataType: "json",
    success: function(resp) {
      // feature should redirect to last used document on dashboard
      window.location.href = "/joyce/loader/";
    },
    error: function(resp) {
      $error.text(resp.responseJSON.error).removeClass("error--hidden");
    }
  });

  e.preventDefault();
});


var upload = document.getElementById("upload");
if (upload) {

  $(document).ready(function(){
    document.getElementById("upload").addEventListener("submit", function(event){
      event.preventDefault(); 

      var formData = new FormData(this); 
      var xhr = new XMLHttpRequest(); 

      document.getElementById("loading").classList.remove("hidden");

      xhr.onreadystatechange = function() {
          if (xhr.readyState == XMLHttpRequest.DONE) {

              document.getElementById("loading").classList.add("hidden");
              location.reload();
          }
      }

      xhr.open(this.method, this.action, true);
      xhr.send(formData);
    });
  });
}

// Called at bottom of script.js so that it is called
// whenever page is reloaded
if (column1) {
  setVisibleContent();
}