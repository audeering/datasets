// Expand rows in Tables table to show preview of each tables content.
//
// Implementation based on https://github.com/chhikaradi1993/Expandable-table-row
//
const toggleRow = (row) => {
    // Toggle visibility of table preview
    row.getElementsByClassName('expanded-row-content')[0].classList.toggle('hide-row');
    // Toggle clicked attribute on clicked table row.
    // This can be used to adjust appearance of clicked table,
    // e.g. remove bottom border
    if (row.className.indexOf("clicked") === -1) {
        row.classList.add("clicked");
    } else {
        row.classList.remove("clicked");
    }
    console.log(event);
}
