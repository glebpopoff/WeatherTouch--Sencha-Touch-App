var overlay = new Ext.Panel({
    // We'll set the image src attribute's value programmatically.
    tpl: "{pred}",
    floating: true,
    modal: true,
    centered: true,
    width: 300,
    height: 250,
    styleHtmlContent: true,
    scroll: false,
    cls: 'htmlcontent',
    // Loadmask is true so we see the loading animation.
    loadmask: true,
    dockedItems: [{
    		dock: 'top',
    		xtype: 'toolbar',
    		title: ''
    }]
});

todaysweather.views.WeatherForecast = Ext.extend(Ext.Panel, {
    layout: 'card',
    
    initComponent: function() {
        
        this.list = new Ext.List({
            cls: 'timeline',
            emptyText   : '<p class="no-searches">Unable to retrieve data</p>',
			disableSelection: true,
            store: weatherForecastStore,
            plugins: [{
                ptype: 'pullrefresh'
            }],
            itemCls: 'weatheritem',
			itemTpl: new Ext.XTemplate(
				'<div class="avatar" style="background-image: url(http://img.weather.weatherbug.com/forecast/icons/localized/50x42/en/trans/{imgIcon}.png)"></div><span class="name">{name}<br/><span class="tertiary">{daydesc}<br/><tpl if="high || low"><tpl if="high">{high}&deg; High<br/></tpl>{low}&deg; Low</tpl></span></span>'
            ),
			listeners: {
				itemtap: function (list, index, element, event) {
					// Grab a reference the record.
					var record = list.getRecord(element);
					overlay.getDockedItems()[0].setTitle(record.data.name);
					// First, we update the the overlay with the proper record (data binding).
					overlay.update(record.data);
					
					// Next we show the overlay.
					overlay.show({type: 'fade', duration: 400})
					
					// Show the loading indicator.
					//overlay.setLoading(true); 
					
				}
			}
	
        });

		fiveDayWeatherForecastToolbar = new Ext.Panel({
            layout: 'fit',
            items: this.list,
            dockedItems: [{
                xtype: 'toolbar',
                title: defaultLocationName
            }
			
			],
            listeners: {
                activate: { fn: function(){
                    //this.list.getSelectionModel().deselectAll();
					//console.log('activate');
                    Ext.repaint();
                }, scope: this }
                
            }
        });
        
        this.items = fiveDayWeatherForecastToolbar;
       	todaysweather.views.WeatherForecast.superclass.initComponent.call(this);
    },
    
    onSelect: function(sel, records){
        if (records[0] !== undefined) {
            
            /*var bioCard = new mytracker.views.MyTeamDetail({
                prevCard: this.listpanel,
                record: records[0]
            });
            
            this.setActiveItem(bioCard, 'slide');
            */
        }
    }
});

Ext.reg('weatherforecast', todaysweather.views.WeatherForecast);
