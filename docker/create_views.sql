-- Create views for SQL tables

-- product
CREATE VIEW insitu_product_view as 
    SELECT p.id as "product_id",
           p.acronym as "product_acronym", 
           p.name as "product_name",
           p.note as "product_note",
           c.name as "product_component",
           a.name as "product_area", 
           pg.name as "product_group",
           ps.name as "product_status",
           ee.name as "product_entrusted_entity",
           cs.name as "product_copernicus_service"
    FROM insitu_product p 
    INNER JOIN insitu_component c ON c.id = p.component_id 
    INNER JOIN picklists_area a ON a.id = p.area_id
    INNER JOIN picklists_productgroup pg ON pg.id = p.group_id
    INNER JOIN picklists_productstatus ps ON ps.id = p.status_id
    INNER JOIN insitu_entrustedentity ee ON ee.id = c.entrusted_entity_id
    INNER JOIN insitu_copernicusservice cs ON cs.id = c.service_id
    WHERE p._deleted = FALSE;

-- productrequirement
CREATE VIEW insitu_productrequirement_view as
    SELECT product_id as "productrequirement_product_id",
           requirement_id as "productrequirement_requirement_id",
           c.name as "productrequirement_criticality",
           dl.name as "productrequirement_level_of_definition",
           r.name as "product_relevance",
           pr.note as "productrequirement_note",
           b.name as "productrequirement_barrier"
    FROM insitu_productrequirement pr
    INNER JOIN picklists_criticality c ON c.id = pr.criticality_id
    INNER JOIN picklists_definitionlevel dl ON dl.id = pr.level_of_definition_id
    INNER JOIN picklists_relevance r ON r.id = pr.relevance_id
    FULL OUTER JOIN insitu_productrequirement_barriers prb ON pr.id = prb.productrequirement_id
    FULL OUTER JOIN picklists_barrier b ON b.id = prb.barrier_id
    WHERE pr._deleted = FALSE;

-- requirement

CREATE VIEW insitu_requirement_view as
    SELECT r.id as "requirement_id",
           r.note as "requirement_note",
           r.name as "requirement_name",
           d.name as "requirement_dissemination",
           uf.threshold as "requirement_update_frequency_threshold",
           uf.breakthrough as "requirement_update_frequency_breakthrough",
           uf.goal as "requirement_update_frequency_goal",
           horizontal_resolution.threshold as "requirement_horizontal_resolution_threshold",
           horizontal_resolution.breakthrough as "requirement_horizontal_resolution_breakthrough",
           horizontal_resolution.goal as "requirement_horizontal_resolution_goal",
           qcp.name as "requirement_quality_control_procedure",
           timeliness.threshold as "requirement_timeliness_threshold",
           timeliness.breakthrough as "requirement_timeliness_breakthrough",
           timeliness.goal as "requirement_timeliness_goal",
           uncertainty.threshold as "requirement_uncertainty_threshold",
           uncertainty.breakthrough as "requirement_uncertainty_breakthrough",
           uncertainty.goal as "requirement_uncertainty_goal",
           vertical_resolution.threshold as "requirement_vertical_resolution_threshold",
           vertical_resolution.breakthrough as "requirement_vertical_resolution_breakthrough",
           vertical_resolution.goal as "requirement_vertical_resolution_goal",
           rp.name as "requirement_group",
           u.first_name || ' ' || u.last_name as "requirement_owner",
           r.state as "requirement_state"
    FROM insitu_requirement r
    INNER JOIN picklists_dissemination d ON d.id = r.dissemination_id
    INNER JOIN insitu_metric uf ON uf.id = r.update_frequency_id 
    INNER JOIN insitu_metric horizontal_resolution ON horizontal_resolution.id =  r.horizontal_resolution_id
    INNER JOIN picklists_qualitycontrolprocedure qcp ON qcp.id = r.quality_control_procedure_id
    INNER JOIN insitu_metric timeliness ON timeliness.id = r.timeliness_id
    INNER JOIN insitu_metric uncertainty ON uncertainty.id = r.uncertainty_id
    INNER JOIN insitu_metric vertical_resolution ON vertical_resolution.id = r.vertical_resolution_id
    INNER JOIN picklists_requirementgroup rp ON rp.id = r.group_id
    INNER JOIN auth_user u ON u.id = r.created_by_id
    WHERE r._deleted = FALSE;

-- datarequirement

CREATE VIEW insitu_datarequirement_view as
    SELECT dr.data_id as "datarequirement_data_id",
           dr.requirement_id as "datarequirement_requirement_id",
           dr.note as "datarequirement_note",
           dr.information_costs  as "datarequirement_information_costs",
           dr.handling_costs as "datarequirement_handling_costs",
           cl.name as "datarequirement_level_of_compliance"
    FROM insitu_datarequirement dr
    INNER JOIN picklists_compliancelevel cl ON cl.id = dr.level_of_compliance_id
    WHERE dr._deleted = FALSE;

-- data

CREATE VIEW insitu_data_view as
    SELECT d.id AS "data_id",
           d.name AS "data_name",
           d.note AS "data_note",
           a.name AS "data_area",
           df.name AS "data_format",
           dt.name AS "data_type",
           uf.name AS "data_update_frequency",
           dp.name AS "data_policy",
           qcp.name AS "data_quality_control_procedure",
           t.name AS "data_timeliness",
           d.start_time_coverage AS "data_start_time_coverage",
           d.end_time_coverage AS "data_end_time_coverage",
           di.name AS "data_dissemination",
           u.first_name || ' ' ||  u.last_name AS "data_owner",
           d.state AS "data_state",
           ev.domain || ' - ' ||  ev.component || ' - ' || ev.parameter AS "data_essential_variable",
           it.annex || ' ' || it.name AS "data_inspiretheme",
           d.created_at AS "data_created_at",
           d.updated_at AS "data_updated_at"
    FROM insitu_data d
    FULL OUTER JOIN picklists_area a ON a.id = d.area_id
    FULL OUTER JOIN picklists_dataformat df ON df.id = d.data_format_id
    FULL OUTER JOIN picklists_datatype dt ON dt.id = d.data_type_id
    FULL OUTER JOIN picklists_updatefrequency uf ON uf.id = d.update_frequency_id
    FULL OUTER JOIN picklists_datapolicy dp ON dp.id = d.data_policy_id
    FULL OUTER JOIN picklists_qualitycontrolprocedure qcp ON qcp.id = d.quality_control_procedure_id
    FULL OUTER JOIN picklists_timeliness t ON t.id = d.timeliness_id
    FULL OUTER JOIN picklists_dissemination di ON di.id = d.dissemination_id
    FULL OUTER JOIN auth_user u ON u.id = d.created_by_id
    FULL OUTER JOIN insitu_data_essential_variables dev ON  d.id = dev.data_id
    FULL OUTER JOIN picklists_essentialvariable ev ON ev.id = dev.essentialvariable_id
    FULL OUTER JOIN insitu_data_inspire_themes dit ON d.id = dit.data_id
    FULL OUTER JOIN picklists_inspiretheme it ON it.id = dit.inspiretheme_id
    WHERE d._deleted = FALSE;

-- insitu_dataproviderrelation

CREATE VIEW insitu_dataproviderrelation_view as
    SELECT dpr.data_id as "dataproviderrelation_data_id",
           dpr.provider_id as "dataproviderrelation_provider_id",
           dpr.role as "dataproviderrelation_role"
    FROM insitu_dataproviderrelation dpr
    WHERE dpr._deleted = FALSE;



-- insitu_dataprovider without networks
CREATE VIEW insitu_dataprovider_without_networks_view as
    SELECT dp.id AS "data_provider_id",
           dpd.acronym AS "data_provider_acronym",
           dp.name AS "data_provider_name",
           dp.is_network AS "data_provider_is_network",
           dpd.website AS "data_provider_website",
           dpd.address AS "data_provider_address",
           dpd.phone AS "data_provider_phone",
           dpd.email AS "data_provider_email",
           dpd.contact_person AS "data_provider_contact_person",
           pt.name AS "data_provider_type",
           dp.state AS "data_provider_state"
    FROM insitu_dataprovider dp
    FULL OUTER JOIN insitu_dataproviderdetails dpd ON dp.id = dpd.data_provider_id
    FULL OUTER JOIN picklists_providertype pt ON pt.id = dpd.provider_type_id
    WHERE dp._deleted = FALSE;


-- insitu_dataprovider
CREATE VIEW insitu_dataprovider_view as
    SELECT dp.id AS "data_provider_id",
           dpd.acronym AS "data_provider_acronym",
           dp.name AS "data_provider_name",
           dp.is_network AS "data_provider_is_network",
           dpd.website AS "data_provider_website",
           dpd.address AS "data_provider_address",
           dpd.phone AS "data_provider_phone",
           dpd.email AS "data_provider_email",
           dpd.contact_person AS "data_provider_contact_person",
           pt.name AS "data_provider_type",
           c.name AS "data_provider_country",
           dpnetwork.name AS "data_provider_network_name",
           dp.state AS "data_provider_state"
    FROM insitu_dataprovider dp
    FULL OUTER JOIN insitu_dataproviderdetails dpd ON dp.id = dpd.data_provider_id
    FULL OUTER JOIN picklists_providertype pt ON pt.id = dpd.provider_type_id
    FULL OUTER JOIN insitu_dataprovider_countries dpc ON dp.id = dpc.dataprovider_id
    FULL OUTER JOIN picklists_country c ON c.code = dpc.country_id
    FULL OUTER JOIN insitu_dataprovider_networks dpn ON dp.id = dpn.from_dataprovider_id
    LEFT OUTER JOIN insitu_dataprovider dpnetwork ON dpnetwork.id = dpn.to_dataprovider_id and dpnetwork._deleted = FALSE
    WHERE dp._deleted = FALSE;
