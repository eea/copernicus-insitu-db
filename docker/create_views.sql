-- Create views for SQL tables

-- product
CREATE VIEW insitu_product_view as 
    SELECT p.id as "product_id",
           p.acronym as "product_acronym", 
           p.name as "product_name",
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
           r.name as "product_relevance"
    FROM insitu_productrequirement pr
    INNER JOIN picklists_criticality c ON c.id = pr.criticality_id
    INNER JOIN picklists_definitionlevel dl ON dl.id = pr.level_of_definition_id
    INNER JOIN picklists_relevance r ON r.id = pr.relevance_id
    WHERE pr._deleted = FALSE;

-- requirement

CREATE VIEW insitu_requirement_view as
    SELECT r.id as "requirement_id",
           r.name as "requirement_name",
           d.name as "requirement_dissemination",
           uf.threshold || ' ' || uf.breakthrough || ' ' || uf.goal as "requirement_update_frequency",
           horizontal_resolution.threshold || ' ' || horizontal_resolution.breakthrough || ' ' || horizontal_resolution.goal as "requirement_horizontal_resolution",
           qcp.name as "requirement_quality_control_procedure",
           timeliness.threshold || ' ' || timeliness.breakthrough || ' ' || timeliness.goal as "requirement_timeliness",
           uncertainty.threshold  || ' ' || uncertainty.breakthrough || ' ' || uncertainty.goal as "requirement_uncertainty",
           vertical_resolution.threshold || ' ' || vertical_resolution.breakthrough || ' ' ||  vertical_resolution.goal as "requirement_vertical_resolution",
           rp.name as "requirement_group",
           u.first_name || ' ' || u.last_name as "requirement_owner"
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
           u.first_name || ' ' ||  u.last_name as "data_owner"
    FROM insitu_data d
    INNER JOIN picklists_area a ON a.id = d.area_id
    INNER JOIN picklists_dataformat df ON df.id = d.data_format_id
    INNER JOIN picklists_datatype dt ON dt.id = d.data_type_id
    INNER JOIN picklists_updatefrequency uf ON uf.id = d.update_frequency_id
    INNER JOIN picklists_datapolicy dp ON dp.id = d.data_policy_id
    INNER JOIN picklists_qualitycontrolprocedure qcp ON qcp.id = d.quality_control_procedure_id
    INNER JOIN picklists_timeliness t ON t.id = d.timeliness_id
    INNER JOIN picklists_dissemination di ON di.id = d.dissemination_id
    INNER JOIN auth_user u ON u.id = d.created_by_id
    WHERE d._deleted = FALSE;

-- insitu_dataproviderrelation

CREATE VIEW insitu_dataproviderrelation_view as
    SELECT dpr.data_id as "dataproviderrelation_data_id",
           dpr.provider_id as "dataproviderrelation_provider_id",
           dpr.role as "dataproviderrelation_role"
    FROM insitu_dataproviderrelation dpr
    WHERE dpr._deleted = FALSE;

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
           pt.name AS "data_provider_type"
    FROM insitu_dataprovider dp
    INNER JOIN insitu_dataproviderdetails dpd ON dp.id = dpd.data_provider_id
    INNER JOIN picklists_providertype pt ON pt.id = dpd.provider_type_id
    WHERE dp._deleted = FALSE;
