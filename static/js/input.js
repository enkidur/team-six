const exerInputElem = document.querySelector('.exer-input');
const exerListElem = document.querySelector('.exer-list');
const completeAllBtnElem = document.querySelector('.complete-all-btn');
const leftItemsElem = document.querySelector('.left-items')
const showAllBtnElem = document.querySelector('.show-all-btn');
const showActiveBtnElem = document.querySelector('.show-active-btn');
const showCompletedBtnElem = document.querySelector('.show-completed-btn');
const clearCompletedBtnElem = document.querySelector('.clear-completed-btn');

document.querySelector('.exer-list').setAttribute("id","exer")

let id = 0;
const setId = (newId) => {
    id = newId
};

let isAllCompleted = false; // 전체 exers 체크 여부
const setIsAllCompleted = (bool) => {
    isAllCompleted = bool
};

let currentShowType = 'all'; // all  | active | complete
const setCurrentShowType = (newShowType) => currentShowType = newShowType

let exers = [];
const setexers = (newexers) => {
    exers = newexers;
}

const getAllexers = () => {
    return exers;
}
const getCompletedexers = () => {
    return exers.filter(exer => exer.isCompleted === true);
}
const getActiveexers = () => {
    return exers.filter(exer => exer.isCompleted === false);
}

const setLeftItems = () => {
    const leftexers = getActiveexers()
    leftItemsElem.innerHTML = `${leftexers.length} items left`
}

const completeAll = () => {
    completeAllBtnElem.classList.add('checked');
    const newexers = getAllexers().map(exer => ({...exer, isCompleted: true}))
    setexers(newexers)
}

const incompleteAll = () => {
    completeAllBtnElem.classList.remove('checked');
    const newexers = getAllexers().map(exer => ({...exer, isCompleted: false}));
    setexers(newexers)
}

// 전체 exers의 check 여부 (isCompleted)
const checkIsAllCompleted = () => {
    if (getAllexers().length === getCompletedexers().length) {
        setIsAllCompleted(true);
        completeAllBtnElem.classList.add('checked');
    } else {
        setIsAllCompleted(false);
        completeAllBtnElem.classList.remove('checked');
    }
}

const onClickCompleteAll = () => {
    if (!getAllexers().length) return; // exers배열의 길이가 0이면 return;

    if (isAllCompleted) incompleteAll(); // isAllCompleted가 true이면 exers를 전체 미완료 처리
    else completeAll(); // isAllCompleted가 false이면 exers를 전체 완료 처리
    setIsAllCompleted(!isAllCompleted); // isAllCompleted 토글
    paintexers(); // 새로운 exers를 렌더링
    setLeftItems()
}

const appendexers = (text) => {
    const newId = id + 1; // 기존에 i++ 로 작성했던 부분을 setId()를 통해 id값을 갱신하였다.
    setId(newId)
    const newexers = getAllexers().concat({id: newId, isCompleted: false, content: text})
    // const newexers = [...getAllexers(), {id: newId, isCompleted: false, content: text }]
    setexers(newexers)
    setLeftItems()
    checkIsAllCompleted();
    paintexers();
}

const deleteexer = (exerId) => {
    const newexers = getAllexers().filter(exer => exer.id !== exerId);
    setexers(newexers);
    setLeftItems()
    paintexers()
}

const completeexer = (exerId) => {
    const newexers = getAllexers().map(exer => exer.id === exerId ? {...exer, isCompleted: !exer.isCompleted} : exer)
    setexers(newexers);
    paintexers();
    setLeftItems()
    checkIsAllCompleted();
}

const updateexer = (text, exerId) => {
    const currentexers = getAllexers();
    const newexers = currentexers.map(exer => exer.id === exerId ? ({...exer, content: text}) : exer);
    setexers(newexers);
    paintexers();
}

const onDbclickexer = (e, exerId) => {
    const exerElem = e.target;
    const inputText = e.target.innerText;
    const exerItemElem = exerElem.parentNode;
    const inputElem = document.createElement('input');
    inputElem.value = inputText;
    inputElem.classList.add('edit-input');
    inputElem.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            updateexer(e.target.value, exerId);
            document.body.removeEventListener('click', onClickBody);
        }
    })

    const onClickBody = (e) => {
        if (e.target !== inputElem) {
            exerItemElem.removeChild(inputElem);
            document.body.removeEventListener('click', onClickBody);
        }
    }

    document.body.addEventListener('click', onClickBody)
    exerItemElem.appendChild(inputElem);
}

const clearCompletedexers = () => {
    const newexers = getActiveexers()
    setexers(newexers)
    paintexers();
}

const paintexer = (exer) => {
    const exerItemElem = document.createElement('li');
    exerItemElem.classList.add('exer-item');

    exerItemElem.setAttribute('data-id', exer.id);

    const checkboxElem = document.createElement('div');
    checkboxElem.classList.add('checkbox');
    checkboxElem.addEventListener('click', () => completeexer(exer.id))

    const exerElem = document.createElement('div');
    exerElem.classList.add('exer');
    exerElem.addEventListener('dblclick', (event) => onDbclickexer(event, exer.id))
    exerElem.innerText = exer.content;

    const delBtnElem = document.createElement('button');
    delBtnElem.classList.add('delBtn');
    delBtnElem.addEventListener('click', () => deleteexer(exer.id))
    delBtnElem.innerHTML = 'X';

    /*완료되면 ✔ 추가*/
    if (exer.isCompleted) {
        exerItemElem.classList.add('checked');
        checkboxElem.innerText = '✔';
    }

    exerItemElem.appendChild(checkboxElem);
    exerItemElem.appendChild(exerElem);
    exerItemElem.appendChild(delBtnElem);

    exerListElem.appendChild(exerItemElem);
}

const paintexers = () => {
    exerListElem.innerHTML = null;

    switch (currentShowType) {
        case 'all':
            const allexers = getAllexers();
            allexers.forEach(exer => {
                paintexer(exer);
            });
            break;
        case 'active':
            const activeexers = getActiveexers();
            activeexers.forEach(exer => {
                paintexer(exer);
            });
            break;
        case 'completed':
            const completedexers = getCompletedexers();
            completedexers.forEach(exer => {
                paintexer(exer);
            });
            break;
        default:
            break;
    }
}

const onClickShowexersType = (e) => {
    const currentBtnElem = e.target;
    const newShowType = currentBtnElem.dataset.type;

    if (currentShowType === newShowType) return;

    const preBtnElem = document.querySelector(`.show-${currentShowType}-btn`);
    preBtnElem.classList.remove('selected');

    currentBtnElem.classList.add('selected')
    setCurrentShowType(newShowType)
    paintexers();
}

const init = () => {
    exerInputElem.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            appendexers(e.target.value);
            exerInputElem.value = '';
        }
    })
    completeAllBtnElem.addEventListener('click', onClickCompleteAll);
    showAllBtnElem.addEventListener('click', onClickShowexersType);
    showActiveBtnElem.addEventListener('click', onClickShowexersType);
    showCompletedBtnElem.addEventListener('click', onClickShowexersType);
    clearCompletedBtnElem.addEventListener('click', clearCompletedexers);
    setLeftItems()
}

init()

function post() {
    let comment = $("#textarea-post").val()
    let today = new Date().toISOString()
    $.ajax({
        type: "POST",
        url: "/posting",
        data: {
            comment_give: comment,
            date_give: today
        },
        success: function (response) {
            $("#modal-post").removeClass("is-active")
						window.location.reload()
        }
    })
}