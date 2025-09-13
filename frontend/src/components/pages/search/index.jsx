// React
import React, { useState, useEffect, useReducer, useMemo, useRef, useCallback } from 'react';
import { atom, useAtom, useSetAtom } from "jotai";
import { useQueryClient } from '@tanstack/react-query';
 
// Components
import ItemCard from "@/components/item_card";
import Selector from "@/components/selector";
import Sign from "@/components/sign";
import Button from "@/components/buttons";
import { RemovableWord, RemovableWordList } from "@/components/removable";
import { RadioChoice } from "@/components/choice";
import { RadioFilter, NumberFilter, SelectorFilter, resetFilterAtomFamily } from "@/components/filters";
import { BoolProperty, NumberProperty, EnumProperty } from "@/components/properties";
import assets, { ResizableAsset } from "@/toolbox/utils/assets/importAllAssets.jsx";
import { LoaderCircle, X } from "lucide-react"
// Utils
import DOMPurify from 'dompurify';

// Strings
import { parseKeywordListString } from "@/toolbox/utils/strings/general.js";

// API
import {
    use_service_catalog_read_async_filtered_catalog,
    use_service_catalog_read_async_items_properties
} from "@/toolbox/api_services/use_service/use_catalog.js";
import {
    use_service_clients_read_async_distributors_names
} from "@/toolbox/api_services/use_service/use_clients.js";
import {
    catalog_read_async_items_properties,
    catalog_read_async_filtered_catalog,
} from "@/toolbox/api_services/queryKeys.js";


import {
    realtime_old30min_cache30min_tryhard,
    manual_mummy_cache30min_notry,
} from "@/toolbox/utils/api/useQueryConfigPatterns.js";
import { mixed, ref } from 'yup';

//TODO: finish search mode functionality
export const searchModeAtom = atom("usual");
export const searchModes = ["usual", "client", "client-api"];



function ClientFilterReset({ clientName, onInit }) {
  const resetSignal = useSetAtom(resetFilterAtomFamily(`${clientName}_filters_group`));

  useEffect(() => {
    onInit(clientName, {
      resetSignal,
      resetGroupId: `filter_group_${clientName}`,
    });
  }, [clientName, resetSignal, onInit]);

  return null; // nothing rendered
}

const SearchPage = () => {

    const qyueryClient = useQueryClient();

    const [ searchMode, setSearchMode ] = useAtom(searchModeAtom);

    
    // FilteredCatalogRequest (matching backend) for service_catalog_read_async_filtered_catalog
    const [ filteredCatalogRequest, setFilteredCatalogRequest ] = useReducer(
        (state, patch) => {
            return {
                ...state,
                ...patch
            };
        },
        {
            query_string: "",           // query_string of FilteredCatalogRequest (backend)
            keywords    : [],           // -//-
            keywords_and: false,        // -//-
            client_names: [],           // ...
            properties_values: "all",
            offset: 0,
            limit: -1,
        }
    );

    // fetch distributors names for search params and filters 
    const { 
        data: distributors_names, 
        isFetching: isDistributorsNamesFetching,
        dataUpdatedAt: distributors_names_updated_at
    } = use_service_clients_read_async_distributors_names({
        config: realtime_old30min_cache30min_tryhard
    });

    // fetch catalog filtered with serach parameters
    const {
        data: filtered_catalog,
        isFetching: isFilteredCatalogFetching,
        dataUpdatedAt: filtered_catalog_updated_at,
        refetch: filtered_catalog_refetch
    } = use_service_catalog_read_async_filtered_catalog({
        body: filteredCatalogRequest,
        config: manual_mummy_cache30min_notry
    });

    // fetch items properties after fetching catalog, "AFTER" is implented with useEffect
    const {
        data: items_properties,
        isFetching: isItemsPropertiesFetching,
        dataUpdatedAt: items_properties_updated_at,
        refetch: items_properties_refetch
    } = use_service_catalog_read_async_items_properties({
        body: { 
            light_items: filtered_catalog?.items?.map(item => ({ 
                item_id: item.item_id, 
                client_name: item.client_name,
                properties_ids: item.properties_ids
            })) || [],
            only_general: false,//get all props. for general search mode - filter only with general filters and show props in item preview
            offset: 0,
            limit: -1
        },
        config: { ...manual_mummy_cache30min_notry}
    });

    const itemsGeneralPropPriceMap = useMemo(() => {
        if(items_properties_updated_at === 0) {
            return {};
        }
        let result_map = {};
        filtered_catalog?.items?.forEach(item => {
            const itemProps = items_properties.items_props_map[item.item_id] || {};
            // Find first property with non-empty value
            // FIXME: make it possible to see all props not first only
            const pricePropertyId = Object.keys(itemProps)
                .filter(id => id.includes("client_order_price_property") && items_properties.items_props_map[item.item_id][id].value)[0] || null;

            result_map[item.item_id] = {
                price: items_properties.items_props_map[item.item_id][pricePropertyId]?.value || 0,
                unit: items_properties.items_props_map[item.item_id][pricePropertyId]?.unit || "RUB"
            };
        });
        // console.table(result_map);
        return result_map;
    }, [items_properties_updated_at]);

    const itemsGeneralPropOrderMap = useMemo(() => {
        if(items_properties_updated_at === 0) {
            return {};
        }
        let result_map = {};
        filtered_catalog?.items?.map(item => {
            const itemProps = items_properties.items_props_map[item.item_id] || {};
            //FIXME: make it possible to see all props not [0] only

            const orderPropertyId = Object.keys(itemProps)
                .filter(id => id.includes("client_minimum_order_amount_property") && items_properties.items_props_map[item.item_id][id].value)[0] || null;

            result_map[item.item_id] = {
                minQuantity: items_properties.items_props_map[item.item_id][orderPropertyId]?.value || 0,
                unit: items_properties.items_props_map[item.item_id][orderPropertyId]?.unit || "pcs"
            };
        });
        // console.table(result_map);
        return result_map;
    }, [items_properties_updated_at]);

    
    
    // FIXME: whilte there is no pagination, fetching the whole catalog could be heavy, add pagination
    const isAbleToSearch = (filteredCatalogRequest.query_string.trim() !== "" || filteredCatalogRequest.keywords.length !== 0) && !isFilteredCatalogFetching && !isDistributorsNamesFetching;
    const isAbleToApplyFilters = filtered_catalog?.filters?.length > 0;
    const isAbleToUseFilters = !(isItemsPropertiesFetching || isFilteredCatalogFetching || !items_properties);
    const isItemsDataFetching = isFilteredCatalogFetching || isItemsPropertiesFetching;
    const [ filterSelectorsActivations, setFilterSelectorsActivations ] = useState([]);
    const [ itemForPreview, setItemForPreview ] = useState(null);
    const generalFilterGroupName = "general_filters_group";
    const allFiltersGroupName = "all_filters_group";
    // w1c reset signals - see how to use in filters components
    const setResetSignalForGeneralFiltersGroup = useSetAtom(resetFilterAtomFamily(generalFilterGroupName));
    const setResetSignalForAllFiltersGroup = useSetAtom(resetFilterAtomFamily(allFiltersGroupName));
    const [ filtersValuesToApply, setFiltersValuesToApply ] = useState({});//schema: { property_id: {value, isDefault } // isDefault let's us filter elements only
    const [ showUnfilterables, setShowUnfilterables ] = useState(false);
    // Reveal filter on property click block
    const [ filterPropIdToBeRevealed, setFilterPropIdToBeRevealed ] = useState(null); //set id when prop is clicked
    const filterPropRefToBeRevealed = useRef(null);
    const filterPropRefToBeRevealedCallback = useCallback((el) => { //while being rendered - filter checks if its him and conditionally assigns ref 
        console.log(`ref callback with ${el}`);
        if(el) { 
            setFilterPropRefWasSet(true); 
            filterPropRefToBeRevealed.current = el;
        }; // after ref is assigned we notice this
    }, []);
    const [ filterPropRefWasSet, setFilterPropRefWasSet] = useState(false); // yes, this
    // Reveal filter on property click block end
    const [clientFiltersGroupMap, setClientFiltersGroupMap] = useState({});

    // This will just return map of client_name -> reset signal for filter group + group name (basically same as client name)
    distributors_names?.map(name => (
    <ClientFilterReset
        key={name}
        clientName={name}
        onInit={({resetSignal, groupName}) =>
            setClientFiltersGroupMap(prev => ({ ...prev, [groupName]: resetSignal }))
        }
    />
    ));

    // Distributors names and filter tabs with their names are connected, if some tab is active distributors-specific filters are shown
    useEffect(() => {
        if(distributors_names_updated_at === 0) {
            return;
        }
        // Reset filter tabs activations
        if(distributors_names?.length > 0) {
            const newActivations = Array(distributors_names.length).fill(false);
            newActivations[0] = true; // general filters is active
            setFilterSelectorsActivations(newActivations);
            setFilteredCatalogRequest({ client_names: distributors_names });
        }
        else {
            setFilterSelectorsActivations([]);
            setFilteredCatalogRequest({ client_names: [] });
        } 
    }, [distributors_names_updated_at]);


    // items_properties query is actually refetches automatically 
    // because body is different due to filtered_catalog
    // but let this function be here unless you truly test it
    useEffect(() => {
        if(filtered_catalog_updated_at === 0) {
            return;
        }
        items_properties_refetch();
    }, [filtered_catalog_updated_at]);

    useEffect(() => {
        if(items_properties_updated_at === 0) {
            return;
        }
        // Reset All filters
        setResetSignalForAllFiltersGroup(true);
        // Set default item for preview
        setItemForPreview(filtered_catalog.items[0] || null);
    }, [items_properties_updated_at]);

    // Focus the filter property input when it is revealed
    useEffect(() => {
        if(!filterPropRefToBeRevealed.current || !filterPropRefWasSet) {
            return;
        }
        console.log(`current ref: ${filterPropRefToBeRevealed.current}`);
        filterPropRefToBeRevealed.current.focus({ preventScroll: true });//for setting up smooth scroll
        filterPropRefToBeRevealed.current.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
        filterPropRefToBeRevealed.current.style.transition = "background-color 200ms ease";
        filterPropRefToBeRevealed.current.style.backgroundColor = "rgba(0, 255, 0, 0.4)";

        setTimeout(() => {
            filterPropRefToBeRevealed.current.style.transition = "background-color 200ms ease";
            filterPropRefToBeRevealed.current.style.backgroundColor = "";
            setFilterPropIdToBeRevealed(null);
            setFilterPropRefWasSet(false);
        }, 500);
    }, [filterPropRefWasSet]);


    const searchItems = () => {
        filtered_catalog_refetch();
    }


    const resetSearchParams = () => {

    }

    const applyFilters = () => {
        setFiltersValuesToApply(prev=>{return {...prev}});
    }

    useEffect(() => {
    }, []);

    // useEffect(() => {
    //     console.table(filtersValuesToApply);
    // }, [filtersValuesToApply]);

    const escapeHtml = (s) => s.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'" :"&#39;"}[m] || ""));
    
    //if the strig is like this - <sometag>*</sometag> then its html
    //FIXME: make aligned
    const isHtmlish = (s) =>  /<([A-Za-z][\w:-]*)(\s[^>]*)?>[\s\S]*<\/\1>|<([A-Za-z][\w:-]*)(\s[^>]*)?\/?>/.test(s.trim());

    return (
        // Search sidebar - Catalog block - Filters sidebar
        <div className="flex h-[92%] p-[20px]">
            {/* Search sidebar */}
            {/* overflow-x-visible is for RemovableWordList component - every "overflowable" parent to be showed through - should have it  */}
            <div className="flex flex-[1_1_0%] max-w-[250px] flex-col bg-itbs-white-blue gap-[10px] p-[10px] rounded-[10px] overflow-x-visible">
                <div className="flex flex-col items-center h-[95px]">
                    <h1 className="text-itbs-title-small text-center">Search</h1>
                </div>
                {/* Search sidebar parameters */}
                <div className="flex flex-col h-fill  gap-[10px] overflow-x-visible">
                    {/* General search input (query_string) */}
                    <div className="flex flex-col items-center w-full gap-[4px]">
                        <h1 className="flex items-start text-left text-itbs-subtitle-small w-full">General Search</h1>
                        <input className="flex bg-white w-full rounded-[5px]  px-[10px] py-[8px]"
                            type="text"
                            placeholder="Phrase, name, property..."
                            onChange={(e) => {
                                setFilteredCatalogRequest({ query_string: e.currentTarget.value.trim()})
                                // console.log(`String ${e.currentTarget.value}`);
                            }}
                            onKeyDown={(e) => {
                                if (e.key === "Enter") {
                                    setFilteredCatalogRequest({ query_string: e.currentTarget.value.trim() })
                                    // e.target.value = "";
                                }
                            }}
                        />
                    </div>
                    {/* Keywords search block (keywords) */}
                    <div className="flex flex-col items-center w-full gap-[4px] overflow-x-visible">
                        {/* Keyword add */}
                        <div className="flex flex-col items-center w-full gap-[4px]">
                            <h1 className="flex items-start text-left text-itbs-subtitle-small w-full">Keyword(s) or ID</h1>
                            <div className="flex items-center w-full justify-between">
                                <input className="flex flex-[1_0_0%] rounded-[5px] bg-white px-[10px] py-[8px]"
                                    type="text"
                                    placeholder="Keywords separated by space or comma"
                                    onKeyDown={(e) => {
                                        if (e.key === "Enter") {
                                           setFilteredCatalogRequest({ keywords: [
                                                ...filteredCatalogRequest.keywords,
                                                ...parseKeywordListString(e.target.value.trim()) 
                                            ]})
                                           e.target.value = "";
                                        }
                                    }}
                                />
                            </div>
                        </div>
                        {/* AND/OR */}
                        <div className="flex items-center w-full">
                            <RadioChoice 
                                onValueChange={(value)=>{
                                    setFilteredCatalogRequest({ keywords_and: value === "AND" })
                                }}
                                options={["AND", "OR"]}
                                defaultValueIndex={0}
                            />
                        </div>
                        {/* Keywords list */}
                        <div className="flex items-center w-full overflow-x-visible">
                            <RemovableWordList 
                                words={filteredCatalogRequest.keywords}
                                onRemove={(wordIndex) => {
                                    const newKeywords = [...filteredCatalogRequest.keywords];
                                    newKeywords.splice(wordIndex, 1);
                                    setFilteredCatalogRequest({ keywords: newKeywords });
                                }}
                                onRemoveAll={() => setFilteredCatalogRequest({ keywords: [] })}
                            />
                        </div>
                    </div>
                    {/* Distributors choice block */}
                    { isDistributorsNamesFetching ? (
                        <div className="flex flex-col items-start w-full">
                            <LoaderCircle className="animate-spin" size={30}/>
                        </div>
                    ) : (
                    // TODO: if only one active sign remains - make it non inactivatable 
                    <div className="flex flex-col items-start w-full gap-[4px]">
                        <h1 className="flex items-start text-itbs-subtitle-small text-left">Distributors</h1>
                        <div className="flex flex-wrap items-start gap-[10px]">
                            {distributors_names.map((name, index) => (
                                <Sign key={index}
                                    text={name}
                                    isActive={true}
                                    onClick={(isActive) => setFilteredCatalogRequest({ 
                                        client_names: isActive ? [...filteredCatalogRequest.client_names, name] 
                                            : filteredCatalogRequest.client_names.filter(n => n !== name) 
                                    })}
                                />
                            ))}
                        </div>
                    </div>
                    )}
                    {/* TODO: Search mode selector */}
                   <div className="flex flex-col items-start w-full gap-[4px]">
                        <h1 className="flex items-start text-itbs-subtitle-small text-left">Search Mode</h1>
                        <Selector
                            options={searchModes}
                            defaultValueIndex={searchModes.indexOf(searchMode)}
                            variant={"search-mode"}
                            onValueChange={(value) => setSearchMode(value)}
                        />
                    </div>
                </div>
                {/* Search sidebar control panel */}
                <div className="flex flex-col items-start mt-[10%] px-[20px] py-[20px] border-t-[0.5px] border-t-itbs-light-gray">
                    {/* search/reset buttons */}
                    <div className="flex items-center justify-between w-full px-[15px]">
                        <Button 
                            text="Search Items"
                            variant="support"
                            subVariant="neutral"
                            onClick={() => {searchItems()}}
                            disabled={!isAbleToSearch}
                        />
                        <span className="hover:cursor-pointer hover:text-itbs-light-blue" onClick={() => resetSearchParams()}>Reset All</span>
                    </div>
                </div>
            </div>
            {/* Catalog block */}
            <div className="flex flex-[3_1_0%] justify-around px-[20px] overflow-y-auto">
                { isItemsDataFetching || !filtered_catalog?.items ? (
                    isItemsDataFetching ?
                    <div className="flex flex-col items-center p-[10%] flex-[2_1_0%]">
                        <LoaderCircle className="animate-spin" size={30}/>
                    </div>
                    :
                    <div className="flex flex-col items-center p-[10%] flex-[2_1_0%]">
                        <h1 className="text-itbs-subtitle-small">No results</h1>
                    </div>
                ) : (
                <>
                {/* Catalog items block 2/3 */}
                <div className="flex flex-[2_1_0%] p-[20px]">
                    <div className="flex flex-col gap-[10px]">
                        <div className="flex flex-col items-center">
                            <h1 className="text-itbs-title-small text-left h-fit w-fit">Catalog({filtered_catalog.items.length || 0})</h1>
                        </div>
                        <div className="flex flex-col gap-[10px]">
                            {/* FIXME: use useMemo */}
                            {filtered_catalog?.items && filtered_catalog.items.length > 0  && items_properties ? (
                                filtered_catalog.items.map((item, index) => {

                                    // Additional filtering by properties
                                    let matchesFilters = true; 
                                    let impossibleToFilter = false;
                                    if (filtersValuesToApply) {
                                        const item_props_ids = item?.properties_ids || []
                                        Object.keys(filtersValuesToApply).forEach(filter_prop_id => {

                                            // NOTE: add more special filters if needed
                                            if (["==<!special_distributors_filter!>=="].includes(filter_prop_id)) {
                                                return;
                                            }

                                            // Filter is not applied?
                                            if(filtersValuesToApply[filter_prop_id].isDefault) {
                                                //nothing to do - show item
                                                return;
                                            }

                                            // If filter is applied:
                                            // Item has according property?
                                            if(!item_props_ids.includes(filter_prop_id)) {
                                                // We don't know what item's property value could be - its not matching filters 
                                                impossibleToFilter = true; 
                                            } 
                                            else {
                                                // If item has according property - filter like usual
                                                const filterValue = filtersValuesToApply?.[filter_prop_id].value;
                                                if (filterValue === undefined || filterValue === null) {
                                                    return; 
                                                }

                                                const prop_type = items_properties.items_props_map[item.item_id][filter_prop_id]?.type;
                                                let prop_value = items_properties.items_props_map[item.item_id][filter_prop_id]?.value;
                                                // Radio filters
                                                if (prop_type === "bool") {
                                                    if (prop_value !== filterValue) {
                                                        matchesFilters = false;
                                                    }
                                                }
                                                else
                                                // Number filters
                                                if (prop_type === "float") {
                                                    prop_value = parseFloat(prop_value); 
                                                    if (prop_value < parseFloat(filterValue.minValue) || prop_value > parseFloat(filterValue.maxValue)) {
                                                        matchesFilters = false;
                                                    }
                                                }
                                                else
                                                // Selection filters
                                                if (prop_type === "str") {
                                                    console.log(`filter value ${filterValue}`);
                                                    if (prop_value !== filterValue && filterValue !== "ALL") {
                                                        matchesFilters = false;
                                                    }
                                                }
                                            }

                                        })
                                    }

                                    if (!matchesFilters) {
                                        return null;
                                    }

                                    let customBg = ""
                                    if (impossibleToFilter) {
                                        if(showUnfilterables) {
                                            return null;
                                        }
                                        customBg = " bg-itbs-light-red "
                                    }

                                    const client_name_filter_val = filtersValuesToApply?.["==<!special_distributors_filter!>=="]?.value;
                                    // console.log(`Client name filter value: ${client_name_filter_val}`);

                                    // filter by client name, if ALL - show 
                                    if(client_name_filter_val && item?.client_name !== client_name_filter_val && client_name_filter_val !== "ALL") {
                                        return null;
                                    }

                                    return (
                                        <div className="flex items-center w-full gap-3"
                                            key={index}
                                            onClick={() => {
                                                if(itemForPreview?.item_id !== item?.item_id || "") {
                                                    setItemForPreview(item);
                                                    console.table(item);
                                                }
                                            }}
                                        >
                                            <ItemCard
                                                name={item?.names[0] || "undefined"}
                                                description={item?.description}
                                                distributor={item?.client_name || "undefined"}
                                                imageSrc={""}
                                                isFocused={itemForPreview?.item_id === item?.item_id || ""}
                                                priceInfo={itemsGeneralPropPriceMap[item.item_id]}
                                                orderInfo={itemsGeneralPropOrderMap[item.item_id]}
                                                interactiveCompareDocsIsActive={false}
                                                interactiveCompareDocsOnClick={() => {}}
                                                interactiveSaveDocIsActive={false}
                                                interactiveSaveDocOnClick={() => {}}
                                                customBg={customBg}
                                            />
                                            <h1 className="text-itbs-annotation-small text-right w-[10px] mt-5 h-fit">{index+1}</h1>
                                        </div>
                                    )
                                })
                            ) : (
                                <div className="flex items-center justify-center h-full">
                                    <h1 className="text-itbs-subtitle-small">No items found</h1>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
                <div className="sticky flex flex-col items-center top-0 h-full py-[2%]">
                    <div className="flex h-full items-center border-l-[2px] border-itbs-light-gray">

                    </div>
                </div>
                {/* Item preview block 1/3 */}
                { itemForPreview && (
                    <div className="sticky top-0 flex justify-center flex-[1_1_0%] overflow-y-auto scrollbar-none px-[20px]">
                        <div className="flex flex-col items-center gap-[10px]">
                            <div className="flex flex-col items-center">
                                <h1 className="text-itbs-title-small text-center h-fit">Item preview</h1>
                            </div>
                            <div className="flex flex-col items-center gap-[10px] = scrollbar-none">
                                <div className="flex justify-center max-w-[256px] border-[1px] border-itbs-dark-gray rounded-[10px]">
                                    <img 
                                        src={items_properties.items_props_map[itemForPreview.item_id]?.["client_item_image_property"]?.value} 
                                        alt={"Item"}
                                        // To change image size - change description,name max-w/min-w below too and item preview root block max-w too
                                        // Formula for descr.,name max-w =img width + 12px (for current text sizes) 
                                        className="max-w-[256px] max-h-[256px] w-[256px] h-[256px]"
                                    />
                                </div>
                                {/* Description, Name */}
                                <div className="flex justify-center flex-col overflow-y-auto scrollbar-none w-full  p-y-[12px] gap-[12px] rounded-[10px] min-w-[268px] min-h-[140px] max-h-[300px]">
                                    <h1 className="text-itbs-annotation-small break-words">{itemForPreview?.names[0]}</h1>
                                    {isHtmlish(itemForPreview?.description) ? 
                                        <h1 className="text-itbs-annotation-small font-itbs-light break-words scrollbar-none max-h-[200px]"
                                            dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(itemForPreview?.description) }}
                                        />
                                        :
                                        <h1 className="text-itbs-annotation-small font-itbs-light break-words overflow-auto scrollbar-none max-h-[200px]">{itemForPreview?.description}</h1>
                                    }
                                </div>
                                {/* Properties */}
                                <div className="flex w-full flex-col gap-[10px] overflow-x-hidden p-y-[12px]">
                                    {
                                        items_properties.items_props_map[itemForPreview.item_id] && (
                                            Object.keys(items_properties.items_props_map[itemForPreview.item_id]).map((property_id, index) => {
                                                const property = items_properties.items_props_map[itemForPreview.item_id][property_id];
                                                if (!property || !property?.value || !property?.type) {
                                                    return null;
                                                }
                                                if (property.type === "bool") {
                                                    return (
                                                        <div className="flex hover:ring-[0.5px] hover:cursor-pointer hover:ring-itbs-light-gray rounded-[3px]"
                                                            key={index} 
                                                            onClick={() => {
                                                                if(filterPropIdToBeRevealed == null) {
                                                                    setFilterPropIdToBeRevealed(property.property_id);
                                                                }
                                                            }}
                                                        >
                                                            <BoolProperty
                                                                name={property.name}
                                                                value={property.value}
                                                                variant="main"
                                                            />
                                                        </div>
                                                    );
                                                }
                                                else
                                                if (property.type === "str") {
                                                    return (
                                                        <div className="flex hover:ring-[0.5px] hover:cursor-pointer hover:ring-itbs-light-gray rounded-[3px]"
                                                            key={index} 
                                                            onClick={() => {
                                                                if(filterPropIdToBeRevealed == null) {
                                                                    setFilterPropIdToBeRevealed(property.property_id);
                                                                }
                                                            }}
                                                        >
                                                            <EnumProperty
                                                                name={property.name}
                                                                options={[property.value]}
                                                                variant="main"
                                                            />
                                                        </div>
                                                    );
                                                }
                                                else
                                                if (property.type === "float") {
                                                    return (
                                                        <div className="flex hover:ring-[0.5px] hover:cursor-pointer hover:ring-itbs-light-gray rounded-[3px]"
                                                            key={index} 
                                                            onClick={() => {
                                                                if(filterPropIdToBeRevealed == null) {
                                                                    setFilterPropIdToBeRevealed(property.property_id);
                                                                }
                                                            }}
                                                        >
                                                            <NumberProperty
                                                                name={property.name}
                                                                value={parseFloat(property.value) || "?"}
                                                                unit={property.unit || "?"} 
                                                                variant="main"
                                                            />
                                                        </div>
                                                    );
                                                }
                                                return null;
                                            })
                                        )
                                    }
                                </div>
                            </div>
                        </div>
                    </div>
                )}
                </>
                )}
            </div>
            {/* Filters sidebar */}
            <div className="flex flex-col flex-[1_1_0%] max-w-[250px] bg-itbs-white-blue rounded-[10px] gap-[10px] p-[10px] ">
                <div className="flex flex-col items-center h-[95px]">
                    <h1 className="text-itbs-title-small text-center">Filters</h1>
                </div>
                {/* Filters sidebar's filter selectors */}
                <div className="flex flex-col h-fill overflow-y-auto scrollbar-none gap-[10px] p-[10px]  overflow-x-hidden">
                    {/* General filters - separately */}
                    <div className="flex items-center w-full">
                        {/* Panel (yes, made from selector) */}
                        <Selector
                            defaultValueIndex={0}
                            options={["General Filters"]}
                            variant={"client-filter"}
                            reverseArrow={true}//its opened in the beginning so arrow should be down
                            elementClassName=" bg-itbs-light-blue "
                            onOpenChange={(value, name, id, isOpen) => {
                                const newActivations = [...filterSelectorsActivations];
                                newActivations[0] = !newActivations[0];
                                setFilterSelectorsActivations(newActivations);
                            }}
                        />
                    </div>
                    

                    {/* General filters - shown by default (shown/hidden on panel click) */}
                    {filterSelectorsActivations[0] && isAbleToUseFilters && (
                    <>
                    {/* Reset button - resets all filters of 'general' group */}
                    <div className="flex justify-center hover:cursor-pointer hover:text-itbs-light-blue"
                        onClick={()  => {setResetSignalForGeneralFiltersGroup(true)}}
                    >
                        <h1 className="text-center text-itbs-annotation-small font-weight-itbs-light"
                        >
                            Reset
                        </h1>
                    </div>
                    {/* Custom filter - not from properties: choose distributor  */}
                    <SelectorFilter
                        propertyName={"Distributor"}
                        propertyId={"==<!special_distributors_filter!>=="}
                        options={["ALL", ...distributors_names?.map((name) => name) || []]}
                        defaultValueIndex={0}
                        resetFilterIds={[generalFilterGroupName, allFiltersGroupName]}
                        onValueChange={(value, name, id) => {
                            console.log(`Setting distributors to ${value}`);
                            setFiltersValuesToApply(prev => ({
                                ...prev,
                                [id]: {value, isDefault:false}
                            }));
                        }}
                        onResetFilter={(value, name, id) => {
                            console.log(`Resetting distributors to ${value}`);
                            setFiltersValuesToApply(prev => ({
                                ...prev,
                                [id]: {value, isDefault:true}
                            }));
                        }}
                    />
                    {/* Show all general filters */}
                    {
                        filtered_catalog?.filters.filter((f) => f.property_id.includes("general")).map((filter, index) => {
                            if (filter.type === "bool") {
                                return (
                                    <RadioFilter
                                        key={filter.property_id}
                                        ref={filterPropIdToBeRevealed === filter.property_id ? filterPropRefToBeRevealedCallback : null}
                                        propertyName={filter.name}
                                        propertyId={filter.property_id}
                                        options={["YES", "NO", "BOTH"]}
                                        defaultValueIndex={2}
                                        resetFilterIds={[generalFilterGroupName, allFiltersGroupName]}
                                        onValueChange={(value, name, id) => {
                                            setFiltersValuesToApply(prev => ({ 
                                                ...prev,
                                                [id]: {value:({"YES":true, "NO":false, "BOTH":null})[value], isDefault:false}
                                            }));
                                        }}
                                        onResetFilter={(value, name, id) => {
                                            setFiltersValuesToApply(prev => ({
                                                ...prev,
                                                [id]: {value:({"YES":true, "NO":false, "BOTH":null})[value], isDefault:true}
                                            }));
                                        }}
                                    />
                                );
                            } else if (filter.type === "float") {
                                return (
                                    <NumberFilter
                                        key={filter.property_id}
                                        ref={filterPropIdToBeRevealed === filter.property_id ? filterPropRefToBeRevealedCallback : null}
                                        propertyName={filter.name}
                                        propertyId={filter.property_id}
                                        unit={filter.unit}
                                        defaultMinValue={parseFloat(filter.min_value)}
                                        defaultMaxValue={parseFloat(filter.max_value)}
                                        resetFilterIds={[generalFilterGroupName, allFiltersGroupName]}
                                        onValueChange={({maxValue, minValue, name, id}) => {
                                            setFiltersValuesToApply(prev => ({
                                                ...prev,
                                                [id]: { value:{maxValue, minValue}, isDefault:false }
                                            }));
                                        }}
                                        onResetFilter={({maxValue, minValue, name, id}) => {
                                            setFiltersValuesToApply(prev => ({
                                                ...prev,
                                                [id]: { value:{maxValue, minValue}, isDefault:true }
                                            }));
                                        }}
                                    />
                                );
                            } else if (filter.type === "str") {
                                return (
                                    <SelectorFilter
                                        key={filter.property_id}
                                        ref={filterPropIdToBeRevealed === filter.property_id ? filterPropRefToBeRevealedCallback : null}
                                        propertyName={filter.name}
                                        propertyId={filter.property_id}
                                        options={["ALL", ...filter.enums]}
                                        defaultValueIndex={0}
                                        resetFilterIds={[generalFilterGroupName, allFiltersGroupName]}
                                        onValueChange={(value, name, id) => {
                                            setFiltersValuesToApply(prev => ({
                                                ...prev,
                                                [id]: {value, isDefault:false}
                                            }));
                                        }}
                                        onResetFilter={(value, name, id) => {
                                            setFiltersValuesToApply(prev => ({
                                                ...prev,
                                                [id]: {value, isDefault:true}
                                            }));
                                        }}
                                    />
                                );
                            }
                        })
                    }
                    </>
                    )}
                    
                    {/* Other filters */}
                    {
                        // FIXME: make it possible to show filters even for several distributors?
                        // NOTE: its not known which filter belongs to which distributor, so all filters are shown, I tried to prevent this wrong behavior here
                        // what is happening here is when items for 1 distributor are shown filters are shown only for those items (which are of single distributor )
                        // now this behavior is correct but we really want filters to be shown together and most probably - merged
                        // need to find a way to do same with filters as with properties in "compare" page. 
                        // 1st step here is definitely change backend to show correct filters available values
                        // 2nd step - find which filter belongs to which distributor
                        // 3rd step - find which filter belongs to which category (which i think is not natural way - correct is on my opinion to show filters for found items. so first find items for some category and filters will be automatically correct)
                        // 4th step thus says to sort filters (or again - maybe beter items first? ) by category (get all categories and find which matches better) with AI
                        // 4.1th step is to get AI help already in merging those sorted filters - for every category (again - its abstract category made by AI based on all existing ones)     
                        // How would merge work? 1. merging only filters with same type
                        distributors_names
                        && filtersValuesToApply?.["==<!special_distributors_filter!>=="]?.value
                        && filtersValuesToApply["==<!special_distributors_filter!>=="].value !== "ALL" 
                        && (filtersValuesToApply?.["==<!special_distributors_filter!>=="]?.value ? [filtersValuesToApply?.["==<!special_distributors_filter!>=="].value] : []).map((client_name, index) => (
                            <div className="flex flex-col items-start w-full gap-[10px]" key={index}>
                                {/* Filter Selector - reveal some if single distributor was chosen */}
                                <div className="flex items-center w-full">
                                    <Selector
                                        defaultValueIndex={0}
                                        options={[client_name]}
                                        variant={"client-filter"}
                                        onOpenChange={(value, name, id, isOpen) => {
                                            const newActivations = [...filterSelectorsActivations];
                                            newActivations[index+1] = !newActivations[index+1];
                                            setFilterSelectorsActivations(newActivations);
                                        }}
                                    />
                                </div>
                                 {/* Show all client specific non-general filters */}
                                {filterSelectorsActivations[index+1] && isAbleToUseFilters && (
                                <>
                                    {/* Reset button - resets all filters of this client_name group */}
                                    <div className="flex justify-center hover:cursor-pointer hover:text-itbs-light-blue"
                                        onClick={()  => {clientFiltersGroupMap[client_name]?.resetSignal(true)}}
                                    >
                                        <h1 className="text-center text-itbs-annotation-small font-weight-itbs-light">
                                            Reset
                                        </h1>
                                    </div>
                                    {filtered_catalog?.filters.filter((f) => !f.property_id.includes("general")).sort((a, b)=>{return a.type.localeCompare(b.type)}).map((filter, index) => {
                                        if (filter.type === "bool") {
                                            return (
                                                <RadioFilter
                                                    key={filter.property_id}
                                                    ref={filterPropIdToBeRevealed === filter.property_id ? filterPropRefToBeRevealedCallback : null}
                                                    propertyName={filter.name}
                                                    propertyId={filter.property_id}
                                                    options={["YES", "NO", "BOTH"]}
                                                    defaultValueIndex={2}
                                                    resetFilterIds={[clientFiltersGroupMap[client_name]?.resetGroupId, allFiltersGroupName]}
                                                    onValueChange={(value, name, id) => {
                                                        setFiltersValuesToApply(prev => ({
                                                            ...prev,
                                                            [id]: {value:({"YES":true, "NO":false, "BOTH":null})[value], isDefault:false}
                                                        }));
                                                    }}
                                                    onResetFilter={(value, name, id) => {
                                                    setFiltersValuesToApply(prev => ({
                                                            ...prev,
                                                            [id]: {value:({"YES":true, "NO":false, "BOTH":null})[value], isDefault:true}
                                                        }));
                                                    }}
                                                />

                                            );
                                        } else if (filter.type === "float") {
                                            return (
                                                <NumberFilter
                                                    key={filter.property_id}
                                                    ref={filterPropIdToBeRevealed === filter.property_id ? filterPropRefToBeRevealedCallback : null}
                                                    propertyName={filter.name}
                                                    propertyId={filter.property_id}
                                                    defaultMinValue={parseFloat(filter.min_value)}
                                                    defaultMaxValue={parseFloat(filter.max_value)}
                                                    resetFilterIds={[clientFiltersGroupMap[client_name]?.resetGroupId, allFiltersGroupName]}
                                                    onValueChange={({maxValue, minValue, name, id}) => {
                                                        setFiltersValuesToApply(prev => ({
                                                            ...prev,
                                                            [id]: { value:{maxValue, minValue}, isDefault:false }
                                                        }));
                                                    }}
                                                    onResetFilter={({maxValue, minValue, name, id}) => {
                                                        setFiltersValuesToApply(prev => ({
                                                            ...prev,
                                                            [id]: { value:{maxValue, minValue}, isDefault:true }
                                                        }));
                                                    }}
                                                />
                                            );
                                        } else if (filter.type === "str") {
                                            return (
                                                <SelectorFilter
                                                    key={filter.property_id}
                                                    ref={filterPropIdToBeRevealed === filter.property_id ? filterPropRefToBeRevealedCallback : null}
                                                    propertyName={filter.name}
                                                    propertyId={filter.property_id}
                                                    options={["ALL", ...filter.enums]}
                                                    defaultValueIndex={0}
                                                    resetFilterIds={[clientFiltersGroupMap[client_name]?.resetGroupId, allFiltersGroupName]}
                                                    onValueChange={(value, name, id) => {
                                                        setFiltersValuesToApply(prev => ({
                                                            ...prev,
                                                            [id]: {value, isDefault:false}
                                                        }));
                                                    }}
                                                    onResetFilter={(value, name, id) => {
                                                        setFiltersValuesToApply(prev => ({
                                                            ...prev,
                                                            [id]: {value, isDefault:true}
                                                        }));
                                                    }}
                                                />
                                            );
                                        }
                                    })}
                                </>
                                )}
                            </div>
                        ))
                    }
                </div>
                {/* Filters sidebar control panel */}
                <div className="flex flex-col items-start mt-[10%] px-[20px] py-[20px] border-t-[0.5px] border-t-itbs-light-gray">
                    {/* apply/reset buttons */}
                    <div className="flex flex-wrap items-center justify-between w-full p gap-[10px] x-[15px]">
                        <Button
                            text="Apply Filters"
                            variant="support"
                            subVariant="neutral"
                            onClick={() => applyFilters()}
                            disabled={!isAbleToApplyFilters}
                        />
                        <span className="hover:cursor-pointer hover:text-itbs-light-blue" onClick={
                            () => setResetSignalForAllFiltersGroup(true)
                        }>
                                Reset All
                        </span>
                        <span className="hover:cursor-pointer hover:text-itbs-light-blue" onClick={
                            () => setShowUnfilterables(prev => !prev)
                        }>
                            {showUnfilterables ?  "Show Unfilterables" : "Hide Unfilterables"}
                        </span>
                    </div>
                </div>
                <h1 className="flex text-itbs-annotation-small font-itbs-light text-right">
                    *Пояснение: при фильтрации товары с отсутствующими свойствами для фильтрации помечены красным цветом как нефильтруемые
                </h1>
            </div>
        </div>
    );
};

export default SearchPage;