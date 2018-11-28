import React, { Component } from 'react';
import './App.css';

import { RadioGroup, RadioButton } from 'react-radio-buttons';

import TimeLineSlider from './TimeLineSlider';
import Checkbox from 'rc-checkbox';
import 'rc-checkbox/assets/index.css';

const colorTable = [
    'red',
    'blue',
    'green',
    'purple',
    '#000000',
    '#CC0066',
    '#339999',
    '#99CCFF',
    '#CCCCCC',
    'yellow',
    'orange',
];

const circles = {};

/* @brief Number of Clustering */
let cCount = 10;

class App extends Component {
    constructor(props) {
        super(props);

        this.cMap = {};

        this.dataSource = [];
        this._data = [];
        this.state = {
            timeInterval: '',
            sliderMinValue: 0,
            sliderMaxValue: 100,
            currentLabel: 0,
            animated: '',

            useTimeLine: false,
            cluster: '0',

            checkedType: []
        };
    }

    componentDidMount() {
        this.fetchResult()
            .then(() => {
                this.init();
                console.log('Loaded.');
            }).catch(e => window.alert(e));
        /*this.fetchCrimeData()
            .then(() => {
                this.init();
                console.log('loaded.');
            }).catch(e => window.alert(e));*/
    }

    fetchResult = async () => {
        let res;
        res = await fetch('/category_map.json');
        this.cMap = await res.json();

        res = await fetch('/result-plot.json');
        let plots = await res.json();
        const _cMap = {};
        for (const [category, digit] of plots) {
            _cMap[digit] = category;
        }
        cCount = 10;
        this.setState({checkedType: new Array(6).fill(true)});

        res = await fetch('/result-data.json');
        this.dataSource = await res.json();
        for (let i in this.dataSource) {
            let _c = this.dataSource[i]['Category'];
            this.dataSource[i]['Category'] = this.cMap[_cMap[_c]]['category']
        }
    }

    fetchCrimeData = async () => {
        const response = await fetch('/crime_robbery_2017.json');
        /**
         * @type {Array<[category: number, distrct: number, hour: number, day: number, month: number, label: number, X: number, Y: number]>}
         */
        this.dataSource = await response.json();
    }
    
    init = () => {
        this.setState({
            timeInterval: 'Hour',
            sliderMinValue: 0,
            sliderMaxValue: 23
        });
        const {checkedType, currentLabel} = this.state;

        this._data = this.dataSource
            .map(({Category, Time, X, Y, ...props}) => {
                const cluster = parseInt(props['class'], 10);
                return {
                    hour: parseInt(Time.slice(0, 2), 10),
                    label: Category,
                    cluster: cluster,
                    center: {lat: parseFloat(Y), lng: parseFloat(X)},
                    radius: 50,
                    fillColor: colorTable[Category]
                };
            });
        const data = this._data
            .filter(({label}) => checkedType[label])
            // .filter(({hour}) => hour === currentLabel);
        this.drawPoints(currentLabel, data);
    }

    /**
     * dragging timeline
     */
    handleSliderChange = (v) => {
        const {checkedType, timeInterval} = this.state;
        let data;
        switch (timeInterval) {
            case 'Hour':
                data = this._data
                    .filter(({hour}) => hour === v)
                    .filter(({label}) => checkedType[label]);
                break;
            default: break;
        }
        if (data) this.drawPoints(v, data);
    }

    // Clear all points at map
    clearPoints = (label) => {
        if (!circles[label]) return;
        circles[label].forEach(circle => {
            circle.setMap(null);
        });
    }

    // draw new points at map
    drawPoints = (label, rawData) => {
        this.clearPoints(this.state.currentLabel);
        this.setState({
            currentLabel: label,
            animated: ' blink'
        }, () => {
            setTimeout(() => {
                this.setState({animated: ''});
            }, 1000);
        });

        let {type, data} = window.drawPoints(rawData);
        switch (type) {
            case 'circle':
                circles[label] = data;
                break;
            default: break;
        }
    }

    /**
     * @param {string} value
     */
    handleSwitchCluster = value => {
        const {checkedType, currentLabel, useTimeLine} = this.state;
        this.setState({cluster: value});
        let data = this._data
            .filter(({label}) => checkedType[label])
            .filter(({cluster}) => cluster === parseInt(value, 10));
        if (useTimeLine) data = data.filter(({hour}) => hour === currentLabel);
        console.log('length', data.length);
        this.drawPoints(currentLabel, data);
    }

    handleUsingTimeLine = e => {
        const checked = e.target.checked;
        let {checkedType, currentLabel, cluster: currentCluster} = this.state;
        currentCluster = parseInt(currentCluster, 10);
        this.setState({useTimeLine: checked});
        let data = this._data
            .filter(({label}) => checkedType[label])
            .filter(({cluster}) => cluster === currentCluster);
        if (checked) data = data.filter(({hour}) => hour === currentLabel);
        this.drawPoints(currentLabel, data);
    }

    /**
     * Select different Label
     */
    handleTypeSelect = (index, checked) => {
        const {checkedType: prevCheckedType, currentLabel, useTimeLine} = this.state;
        let checkedType = [...prevCheckedType];
        checkedType[index] = checked;
        this.setState({checkedType});
        let data = this._data
            .filter(({label}) => checkedType[label]);
        if (useTimeLine) data = data.filter(({hour}) => hour === currentLabel);
        this.drawPoints(currentLabel, data);
    }

    render() {
        const {
            timeInterval, currentLabel, sliderMinValue, sliderMaxValue,
            checkedType, animated, cluster, useTimeLine
        } = this.state;
        return (
        <div className="App">
            <div className="drawer__layout">
                <span className="title">Time Interval</span>
                <span className="content">By {timeInterval}</span>
                <span className="title">Time Period</span>
                {useTimeLine ?
                   <span className={`content${animated}`}>{`${currentLabel}:00 - ${currentLabel + 1}:00`}</span> :
                <span className="content">00:00 - 24:00</span>}
                <div>
                    <Checkbox checked={useTimeLine}
                        onChange={this.handleUsingTimeLine} />
                    <span>Using TimeLine</span>
                </div>
                <span className="title">Cluster</span>
                <div className="clusterTable">
                    <RadioGroup onChange={ this.handleSwitchCluster } value={cluster} >
                        {new Array(cCount).fill(0).map((_, i) =>
                            <RadioButton key={i} value={`${i}`}>Cluster {i + 1}</RadioButton>)}
                    </RadioGroup>
                </div>
                <span className="title">Crime Category</span>
                <div className="colorTable">
                    {this.cMap['mapping'] && colorTable.slice(0, 6).map((value, index) =>
                        <div key={value} className="color__item">
                            <Checkbox checked={checkedType[index]}
                                onChange={(e) => this.handleTypeSelect(index, e.target.checked)} />
                            <span className="color__dot" style={{backgroundColor: value}}></span>
                            <span>{this.cMap['mapping'][index]}</span>
                        </div>
                        )}
                </div>
            </div>
            {useTimeLine &&
                <TimeLineSlider useRange={false} onUpdate={this.handleSliderChange}
                    min={sliderMinValue} max={sliderMaxValue} /> }
        </div>
        );
    }
}

export default App;
