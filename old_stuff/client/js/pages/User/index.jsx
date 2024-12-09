import React from 'react';

export default class User extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            games_list: {},
            image: undefined
        };
    }
    componentDidMount() {
        fetch('/user_info').then((response) => response.json())
        .then(obj => {
            this.setState({
                games_list: {
                    ...obj.games_list,
                    ...this.state.games_list
                }
            });
        });
        fetch('/user_graph').then((response) => response.blob())
        .then(obj => {
            this.setState({
                image: URL.createObjectURL(obj)
            });
        });
    }
    render () {
        return (
            <>
                <div style={{color: 'white'}}>
                    <span>Количество сыгранных игр: {Object.entries(this.state.games_list).length}</span>
                    {
                        Object.entries(this.state.games_list).map((a, i) => 
                            <div key={i}>Номер: {a[0]} Цвет: {a[1].is_white} Результат: {a[1].outcome}</div>
                        )
                    }
                </div>
                <div>
                    {
                        <img src={this.state.image}/>
                    }
                </div>
            </>
            
        );
    }
}
