/**
 * Created by: Andrey Polyakov (andrey@polyakov.im)
 */
import '@styles/styles.less';
import '@styles/styles.scss';

import React from 'react';
import ReactDom from 'react-dom';
import {Provider} from 'react-redux';
import {Store, createStore} from 'redux';

import {ShowReducer} from '@src/reducers';

import {App} from '@components/app/app';

const store = createStore([ShowReducer]);
ReactDom.render(
    <Provider store={store}>
        <App />
    </Provider>,

    document.getElementById('root'),
);
