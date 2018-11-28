import React from 'react';
import ReactDOM from 'react-dom';

import Slider, { createSliderWithTooltip, Range } from 'rc-slider';
import 'rc-slider/assets/index.css';

const ToolTipSlider = createSliderWithTooltip(Slider);

class TimeLineSlider extends React.Component {
    constructor(props) {
        super(props);
        this.state = {

        };
    }

    render() {
        const { useRange, min, max } = this.props;
        return ReactDOM.createPortal(
            <div className="slider__layout">
                {useRange ?
                    <Range /> :
                    <ToolTipSlider min={min} max={max} /*onAfterChange={this.props.onUpdate}*/
                        onChange={this.props.onUpdate} />}
            </div>,
            document.getElementById('slider')
        )
    }
}

export default TimeLineSlider;
