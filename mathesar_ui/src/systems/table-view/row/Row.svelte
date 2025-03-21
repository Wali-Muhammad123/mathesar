<script lang="ts">
  import {
    getCellKey,
    getTabularDataStoreFromContext,
    isNewRecordRow,
    isPlaceholderRow,
    rowHasRecord,
    isGroupHeaderRow,
    isHelpTextRow,
    getRowKey,
    ID_ROW_CONTROL_COLUMN,
    type Row,
  } from '@mathesar/stores/table-data';
  import {
    SheetRow,
    SheetCell,
    isRowSelected,
  } from '@mathesar/components/sheet';
  import { rowHeightPx } from '@mathesar/geometry';
  import { ContextMenu } from '@mathesar/component-library';
  import NewRecordMessage from './NewRecordMessage.svelte';
  import GroupHeader from './GroupHeader.svelte';
  import RowCell from './RowCell.svelte';
  import RowControl from './RowControl.svelte';
  import RowContextOptions from './RowContextOptions.svelte';

  export let row: Row;
  export let style: { [key: string]: string | number };

  const tabularData = getTabularDataStoreFromContext();

  $: ({ recordsData, columnsDataStore, meta, processedColumns, selection } =
    $tabularData);
  $: ({
    rowStatus,
    rowCreationStatus,
    cellModificationStatus,
    cellClientSideErrors,
  } = meta);
  $: ({ grouping, recordSummaries } = recordsData);

  $: ({ pkColumn } = columnsDataStore);
  $: primaryKeyColumnId = $pkColumn?.id;
  $: rowKey = getRowKey(row, primaryKeyColumnId);
  $: creationStatus = $rowCreationStatus.get(rowKey)?.state;
  $: status = $rowStatus.get(rowKey);
  $: wholeRowState = status?.wholeRowState;
  $: ({ selectedCells } = selection);
  $: isSelected = rowHasRecord(row) && isRowSelected($selectedCells, row);
  $: hasWholeRowErrors = wholeRowState === 'failure';
  /** Including whole row errors and individual cell errors */
  $: hasAnyErrors = !!status?.errorsFromWholeRowAndCells?.length;

  function checkAndCreateEmptyRow() {
    if (isPlaceholderRow(row)) {
      void recordsData.addEmptyRecord();
    }
  }

  const handleRowMouseDown = () => {
    if (rowHasRecord(row) && !isPlaceholderRow(row)) {
      selection.onRowSelectionStart(row);
    }
  };

  const handleRowMouseEnter = () => {
    if (rowHasRecord(row) && !isPlaceholderRow(row)) {
      selection.onMouseEnterRowHeaderWhileSelection(row);
    }
  };
</script>

<SheetRow {style} let:htmlAttributes let:styleString>
  <div
    class="row"
    class:selected={isSelected}
    class:processing={wholeRowState === 'processing'}
    class:failed={hasWholeRowErrors}
    class:created={creationStatus === 'success'}
    class:is-new={isNewRecordRow(row)}
    class:is-group-header={isGroupHeaderRow(row)}
    class:is-add-placeholder={isPlaceholderRow(row)}
    {...htmlAttributes}
    style="--cell-height:{rowHeightPx - 1}px;{styleString}"
    on:mousedown={checkAndCreateEmptyRow}
  >
    <SheetCell
      columnIdentifierKey={ID_ROW_CONTROL_COLUMN}
      isStatic
      isControlCell
      let:htmlAttributes={cellHtmlAttr}
      let:style
    >
      <div
        {...cellHtmlAttr}
        {style}
        on:mousedown={handleRowMouseDown}
        on:mouseenter={handleRowMouseEnter}
      >
        {#if rowHasRecord(row)}
          <RowControl
            {primaryKeyColumnId}
            {row}
            {meta}
            {recordsData}
            {isSelected}
            hasErrors={hasAnyErrors}
          />
          <ContextMenu>
            <RowContextOptions recordId={Number(rowKey)} {recordsData} {row} />
          </ContextMenu>
        {/if}
      </div>
    </SheetCell>

    {#if isHelpTextRow(row)}
      <NewRecordMessage columnCount={$processedColumns.size} />
    {:else if isGroupHeaderRow(row) && $grouping && row.group}
      <GroupHeader
        {row}
        grouping={$grouping}
        group={row.group}
        processedColumnsMap={$processedColumns}
        recordSummariesForSheet={$recordSummaries}
      />
    {:else if rowHasRecord(row)}
      {#each [...$processedColumns] as [columnId, processedColumn] (columnId)}
        <RowCell
          {selection}
          {row}
          rowHasErrors={hasWholeRowErrors}
          key={getCellKey(rowKey, columnId)}
          modificationStatusMap={cellModificationStatus}
          clientSideErrorMap={cellClientSideErrors}
          bind:value={row.record[columnId]}
          {processedColumn}
          {recordsData}
        />
      {/each}
    {/if}
  </div>
</SheetRow>

<style lang="scss">
  .row {
    &.processing {
      pointer-events: none;
    }

    &:not(:hover) :global(.cell-bg-row-hover) {
      display: none;
    }

    &.is-add-placeholder {
      cursor: pointer;

      :global([data-sheet-element='cell']:not(.is-active)
          .cell-fabric
          .cell-wrapper
          > *) {
        visibility: hidden;
      }
    }
  }
</style>
