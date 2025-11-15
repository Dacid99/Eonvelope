function getAllSelected() {
  return selectedCheckboxes = document.querySelectorAll('input[data-id]:checked');
}

function setAllSelectionsTo(checked) {
  document.querySelectorAll('input[data-id]').forEach(input => {
    input.checked = checked;
  });
}

function multiDelete(button) {
  const url = new URL(button.dataset.url, window.location.origin);
  const selected = Array.from(getAllSelected());
  const deleteRequests = selected.map(input => {
    const id = input.dataset.id;
    if (id) {
      const itemUrl = buildApiDetailUrl(url, id);
      const request = new Request(itemUrl,
        {
          method: 'DELETE',
          headers: {
            'X-CSRFToken': Cookies.get('csrftoken')
          },
          credentials: 'include',
          mode: 'same-origin'
        }
      );
      return fetch(request).catch(error => { console.log(error.message); });
    }
    return null;
  }).filter(Boolean);

  Promise.all(deleteRequests)
    .then(() => {
      setAllSelectionsTo(false);
      window.location.reload();
    });
}

function multiDownload(button) {
  const url = new URL(button.dataset.url, window.location.origin);
  selected = getAllSelected();
  if (selected) {
    selected.forEach(input => {
      url.searchParams.append('id', input.dataset.id);
    });
    window.open(url, target = '_blank');
    setAllSelectionsTo(false);
  }
}

function multiPost(button) {
  const baseurl = new URL(button.dataset.url, window.location.origin);
  const action = button.dataset.action;

  const selected = Array.from(getAllSelected());
  const requests = selected.map(input => {
    const id = input.dataset.id;
    if (id && action) {
      const url = buildApiDetailActionUrl(baseurl, id, action);
      const request = new Request(url,
        {
          method: 'POST',
          headers: {
            'X-CSRFToken': Cookies.get('csrftoken')
          },
          credentials: 'include',
          mode: 'same-origin'
        }
      );
      return fetch(request).catch(error => { console.log(error.message); });
    }
    return null;
  }).filter(Boolean);

  Promise.all(requests)
    .then(() => {
      setAllSelectionsTo(false);
      window.location.reload();
    });
}
