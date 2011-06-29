todaysweather.views.AddNewLocation = Ext.extend(Ext.Panel, {
    scroll: 'vertical',
    showSessionData: true,
    initComponent: function(){
        this.dockedItems = [{
            xtype: 'toolbar',
            title: 'My Locations',
            items: [{
                ui: 'back',
                text: 'Back',
                scope: this,
                handler: function(){
                    this.ownerCt.setActiveItem(this.prevCard, 'slide');
                }
            },
			{xtype: 'spacer'},
			{
                text: ' Save ',
                ui: 'confirm',
                handler: function() {
					if (formFields.stateField.getValue() || formFields.zipField.getValue())
					{
						try
						{
							Ext.getBody().mask('Saving...', 'x-mask-loading', false);
							console.log('Submitting Data: State=' + formFields.stateField.getValue() + ';Zip=' + formFields.zipField.getValue());
                        	Ext.Ajax.request({
	                            url: '/save?zip=' + formFields.zipField.getValue() + '&statetown=' + formFields.stateField.getValue() + '&lat=' + gpsCoords.lat + '&lon=' + gpsCoords.lon,
	                            success: function(response, opts) {
									var jsonObj = (response.responseText && response.responseText.indexOf('success') != -1) 
												? eval("(" + response.responseText + ")") : null;
									if (jsonObj && jsonObj.status == 'success')
									{
										console.log('successfully saved location: ' + response.responseText);
										
										//update screen titles
										todayWeatherForecastToolbar.getDockedItems()[0].setTitle(jsonObj.location);
										fiveDayWeatherForecastToolbar.getDockedItems()[0].setTitle(jsonObj.location);
								
										//clear current drop-down
										Ext.StoreMgr.clear(locationAjaxStore);
							
										//reload location drop-down
										locationAjaxStore.load();
										//get first element
										//console.log(locationAjaxStore.getAt(0).get('location'));
							
										//reload weather
										weatherForecastStore.proxy.url = '/weather?loc=' + jsonObj.zip;
										weatherForecastStore.load();
							
										//show first screen
										todaysweather.App.setActiveItem(0, 'flip');
								
										todaysweather.App.doLayout();
										//listPanelDropDown.doComponentLayout();
									} else
									{
										Ext.Msg.alert('', 'Unable to save location', Ext.emptyFn);
									}
	                            }
	                        });

							Ext.getBody().unmask();
						} catch (Exception)
						{
							Ext.Msg.alert('', 'Unable to save location', Ext.emptyFn);
						}
					} else
					{
						Ext.Msg.alert('', 'Enter Zip or City/State', Ext.emptyFn);
					}
				}
			}
			]
		}];        
        submitOnAction: false;
        this.items = [
		{
            xtype: 'fieldset',
			title: 'Add New Location',
			instructions: 'Enter ZIP, City/State, or Location',
			items: [
					formFields.zipField,
        			formFields.stateField,
					{
	                       xtype: 'checkboxfield',
	                       name : 'use_mylocation',
	                       label: 'Use GPS',
							value: 0,
	                       useClearIcon: true,
	                       autoCapitalize : false,
						listeners: {
							check: function()
							{
								console.log('Getting GPS Coordinates');
								/*
								//HTML5 geo location
								//better use sencha wrapper api - much easier
								if (navigator.geolocation) 
								{
									Ext.getBody().mask('Loading...', 'x-mask-loading', false);
									navigator.geolocation.getCurrentPosition( 

										function (position) {  
												
												});
												
												}, 
												function (error)
												{
													switch(error.code) 
													{
														case error.TIMEOUT:
															console.log ('Timeout');
															break;
														case error.POSITION_UNAVAILABLE:
															console.log ('Position unavailable');
															break;
														case error.PERMISSION_DENIED:
															console.log ('Permission denied');
															break;
														case error.UNKNOWN_ERROR:
															console.log ('Unknown error');
															break;
													}
												}
											);
											
										Ext.getBody().unmask();	
									}
									*/
									
								var geoService = new Ext.util.GeoLocation({
								            autoUpdate: false
								        });
								geoService.on('beforelocationupdate', 
									function()
									{
								        Ext.getBody().mask('Loading...', 'x-mask-loading', false);
								    }
								, this);
								geoService.on('locationupdate', 
									function(coords) 
									{
										console.log('Lat=' + coords.latitude + ',Long=' + coords.longitude);
										gpsCoords.lat = coords.latitude;
										gpsCoords.lon = coords.longitude
										Ext.getBody().mask('Loading...', 'x-mask-loading', false);
										Ext.Ajax.request({
				                            url: '/geo?ll=' + coords.latitude + ',' + coords.longitude,
				                            success: function(response, opts) {
												var jsonObj = (response.responseText && response.responseText.indexOf('success') != -1) 
															? eval("(" + response.responseText + ")") : null;
												if (jsonObj && jsonObj.status == 'success')
												{
													formFields.zipField.setValue(jsonObj.zip);
													formFields.stateField.setValue(jsonObj.city + ',' + jsonObj.state);
												} else 
												{
													Ext.Msg.alert('Error', 'Unable to retrieve zipcode based on GPS', Ext.emptyFn);
								                }
											}
										});
										Ext.getBody().unmask();
										
										//ok, this stopped working one day
										//google maps api service returns 610 error
										//for the same key I'm using from python requests
										//no idea why the google maps api stopped working from the client side?
										/*console.log('Calling Google Maps Reverse Geo service...')
										Ext.getBody().mask('Loading...', 'x-mask-loading', false);
										    Ext.util.JSONP.request({
							                	url: 'http://maps.google.com/maps/geo',
								                callbackKey: 'callback',
								                params: {                    
								                    output: 'json',
								                    oe: 'utf-8',
													sensor: 'true',
								                    ll: coords.latitude + ',' + coords.longitude,
													key: apiKey
								                },
								                callback: function(result) {
								                    var placemarkData = result.Placemark;
													if (placemarkData) {
														
														var state = placemarkData[0].AddressDetails.Country.AdministrativeArea.AdministrativeAreaName;
														var city = placemarkData[0].AddressDetails.Country.AdministrativeArea.Locality.LocalityName;
														var zip = placemarkData[0].AddressDetails.Country.AdministrativeArea.Locality.PostalCode.PostalCodeNumber;
														console.log('Geo Data: ' + city + ',' + state + ' ' + zip);    
								                  		formFields.zipField.setValue(zip);
														formFields.stateField.setValue(city + ',' + state);
								                    }
								                    else {
														Ext.Msg.alert('Error', 'Unable to retrieve zipcode based on GPS', Ext.emptyFn);
								                    }
								                    Ext.getBody().unmask();
								                }
							            });*/
									
									}
								, this);
								geoService.updateLocation();
								
							}
						}
					}
					]
        }];
		todaysweather.views.AddNewLocation.superclass.initComponent.call(this);
	}
	});

	Ext.reg('addnewlocation', todaysweather.views.AddNewLocation);