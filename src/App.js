import React, { Component } from 'react';
import './App.css';

import TimeLineSlider from './TimeLineSlider';
import Checkbox from 'rc-checkbox';
import 'rc-checkbox/assets/index.css';

const colorTable = [
    'blue',
    'red',
    'purple'
];

const circles = {};

class App extends Component {
    constructor(props) {
        super(props);
        this.dataSource = [];
        this._data = [];
        this.state = {
            timeInterval: '',
            sliderMinValue: 0,
            sliderMaxValue: 100,
            currentLabel: 0,
            animated: '',

            checkedType: [false, true, false]
        };
    }

    componentDidMount() {
        this.fetchCrimeData()
            .then(() => {
                this.init();
                console.log('loaded.');
            }).catch(e => window.alert(e));
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
            .map(record => {
                record.length = 8;
                const [distrct, hour, day, month, label, X, Y] = Array.from(record);
                return {
                    hour: hour,
                    label: label, 
                    center: {lat: Y, lng: X},
                    radius: 50,
                    fillColor: colorTable[label]
                };
            });
        const data = this._data
            .filter(({label}) => checkedType[label])
            .filter(({hour}) => hour === currentLabel)
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
     * Select different Class
     */
    handleTypeSelect = (index, checked) => {
        const {checkedType: prevCheckedType, currentLabel} = this.state;
        let checkedType = [...prevCheckedType];
        checkedType[index] = checked;
        this.setState({checkedType});
        const data = this._data
            .filter(({label}) => checkedType[label])
            .filter(({hour}) => hour === currentLabel);
        this.drawPoints(currentLabel, data);
    }

    render() {
        const {timeInterval, currentLabel, sliderMinValue, sliderMaxValue, checkedType, animated} = this.state;
        return (
        <div className="App">
            <div className="drawer__layout">
                <span className="title">Time Interval</span>
                <span className="content">By {timeInterval}</span>
                <span className="title">Time Period</span>
                <span className={`content${animated}`}>{`${currentLabel}:00 - ${currentLabel + 1}:00`}</span>
                <span className="title">Cluster</span>
                <div className="colorTable">
                    {colorTable.map((value, index) =>
                        <div key={value} className="color__item">
                            <Checkbox checked={checkedType[index]}
                                onChange={(e) => this.handleTypeSelect(index, e.target.checked)} />
                            <span className="color__dot" style={{backgroundColor: value}}></span>
                            <span>Cluster {index + 1}</span>
                        </div>
                        )}
                </div>
                <span className="title">Crime Category</span>
                <span className="content">Robbery</span>
                <span className="title">Crime Data Year</span>
                <span className="content">2017</span>
            </div>
            <TimeLineSlider useRange={false} onUpdate={this.handleSliderChange}
                min={sliderMinValue} max={sliderMaxValue} />
        </div>
        );
    }
}

export default App;
